import sublime
import sublime_plugin
import threading
import re

class Typo3FluidSyntaxToggle(sublime_plugin.EventListener):

	TAG_STANDALONE_REGEX = "<([a-zA-Z]+:[a-zA-Z\.]+)\s+([^>]*)\s+\/>"
	TAG_CLASSIC_REGEX =    "<([a-zA-Z]+:[a-zA-Z\.]+)\s+([^>]*)>(.*)<\/\1>"
	INLINE_REGEX =         "{([a-zA-Z]+:[a-zA-Z\.]+)\(([^}]*)\)}"
	DEFAULT_MAX_TAGS = 200
	SETTINGS_FILENAME = 'Typo3Powerup.sublime-settings'

	tags_for_view = {}
	scopes_for_view = {}
	ignored_views = []
	highlight_semaphore = threading.Semaphore()

	def on_activated(self, view):
		self.update_tag_highlights(view)

	# Async listeners
	def on_load_async(self, view):
		self.update_fluid_tags_async(view)

	def on_modified_async(self, view):
		self.update_fluid_tags_async(view)

	def on_close(self, view):
		for map in [self.tags_for_view, self.scopes_for_view, self.ignored_views]:
			if view.id() in map:
				del map[view.id()]

	"""The logic entry point. Find all URLs in view, store and highlight them"""
	def update_tag_highlights(self, view):
		settings = sublime.load_settings(Typo3FluidSyntaxToggle.SETTINGS_FILENAME)
		should_highlight_tags = settings.get('highlight_tags', True)

		max_tag_limit = settings.get('max_tag_limit', Typo3FluidSyntaxToggle.DEFAULT_MAX_TAGS)

		if view.id() in Typo3FluidSyntaxToggle.ignored_views:
			return

		tags = view.find_all(Typo3FluidSyntaxToggle.TAG_STANDALONE_REGEX + '|' + Typo3FluidSyntaxToggle.INLINE_REGEX)
		print(tags)

		# Avoid slowdowns for views with too much URLs
		if len(tags) > max_tag_limit:
			print("Typo3FluidSyntaxToggle: ignoring view with %u URLs" % len(tags))
			Typo3FluidSyntaxToggle.ignored_views.append(view.id())
			return

		Typo3FluidSyntaxToggle.tags_for_view[view.id()] = tags

		should_highlight_tags = sublime.load_settings(Typo3FluidSyntaxToggle.SETTINGS_FILENAME).get('highlight_tags', True)
		if (should_highlight_tags):
			self.highlight_tags(view, tags)

	"""Same as update_tag_highlights, but avoids race conditions with a	semaphore."""
	def update_fluid_tags_async(self, view):
		Typo3FluidSyntaxToggle.highlight_semaphore.acquire()
		try:
			self.update_tag_highlights(view)
		finally:
			Typo3FluidSyntaxToggle.highlight_semaphore.release()

	"""Creates a set of regions from the intersection of tags and scopes, underlines all of them."""
	def highlight_tags(self, view, tags):
		# We need separate regions for each lexical scope for ST to use a proper color for the underline
		scope_map = {}
		for tag in tags:
			scope_name = view.scope_name(tag.a)
			scope_map.setdefault(scope_name, []).append(tag)

		for scope_name in scope_map:
			self.underline_regions(view, scope_name, scope_map[scope_name])

		self.update_view_scopes(view, scope_map.keys())

	"""Apply underlining with provided scope name to provided regions."""
	def underline_regions(self, view, scope_name, regions):
		if sublime.version() >= '3019':
			# in Sublime Text 3, the regions are just underlined
			view.add_regions(
				u'clickable-tags ' + scope_name,
				regions,
				scope_name,
				flags=sublime.DRAW_NO_FILL|sublime.DRAW_NO_OUTLINE|sublime.DRAW_STIPPLED_UNDERLINE)
		else:
			print('No support for Sublime text version < 3')

	"""Store new set of underlined scopes for view. Erase underlining from
	scopes that were used but are not anymore."""
	def update_view_scopes(self, view, new_scopes):
		old_scopes = Typo3FluidSyntaxToggle.scopes_for_view.get(view.id(), None)
		if old_scopes:
			unused_scopes = set(old_scopes) - set(new_scopes)
			for unused_scope_name in unused_scopes:
				view.erase_regions(u'clickable-tags ' + unused_scope_name)

		Typo3FluidSyntaxToggle.scopes_for_view[view.id()] = new_scopes



def transform_tag(tag):
	print('transform_tag()')
	print(tag)
	if (tag[:1] == '<'):
		m = re.match(r'' + Typo3FluidSyntaxToggle.TAG_STANDALONE_REGEX, tag)
		# print()
		# print(str(m.group(0)))
		# print()

		tagName = m.group(1)
		tagAttributes = m.group(2)

		tagAttributes = re.sub(r'{(.*)}', lambda matchObj: transform_object(matchObj), tagAttributes)
		tagAttributes = re.sub(r'=', ':', tagAttributes)
		tagAttributes = re.sub(r'"', '\'', tagAttributes)
		tagAttributes = re.sub(r' ', ',', tagAttributes)

		tag = '{' + tagName + '(' + tagAttributes.strip() + ')}'
	else:
		m = re.match(r'' + Typo3FluidSyntaxToggle.INLINE_REGEX, tag)
		# print()
		# print(str(m.group(0)))
		# print()

		tagName = m.group(1)
		tagAttributes = m.group(2)

		tagAttributes = re.sub(r':', '=', tagAttributes)
		tagAttributes = re.sub(r'\'', '"', tagAttributes)
		tagAttributes = re.sub(r',', ' ', tagAttributes)

		tag = '<' + tagName + ' ' + tagAttributes + ' />'
	print(tag)
	return tag

#
# {xxx:yyy,aaa:bbb} -> {xxx:\'{yyy}\',aaa:\'{bbb}\'}}
#
def transform_object(matchObj):
	obj = matchObj.group(0)
	obj = re.sub(r' ', '', obj)
	obj = re.sub(r'[a-zA-Z]+:[a-zA-Z]+', lambda matchObj: transform_object_property(matchObj), obj)
	return obj

#
# xxx:yyy -> xxx:\'{yyy}\'
#
def transform_object_property(matchObj):
	prop = matchObj.group(0)
	prop = re.sub(r':([a-zA-Z]+)', ':\\\'{\\1}\\\'', prop)
	return prop


class ToggleTypo3FluidSyntaxUnderCursorCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		if self.view.id() in Typo3FluidSyntaxToggle.tags_for_view:
			selection = self.view.sel()[0]
			if selection.empty():
				selection = next((tag for tag in Typo3FluidSyntaxToggle.tags_for_view[self.view.id()] if tag.contains(selection)), None)
				if not selection:
					return
			print(selection)
			tagBefore = self.view.substr(selection)
			tagAfter = transform_tag(tagBefore)
			self.view.replace(edit, selection, tagAfter)
