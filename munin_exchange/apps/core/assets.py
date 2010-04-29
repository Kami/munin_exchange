from django_assets import Bundle, register

## CSS ##
css_base_bundle = Bundle('css/style.css',
						'css/jquery.notifyBar.css',
						'css/jquery.autocomplete.css',
						'css/jquery.rating.css',
						'css/tipTip.css',
						'css/boxy.css',
						filters = 'yui_css', output = 'css/gen/packed.base.css')
register('css_base', css_base_bundle)

css_sh_bundle = Bundle('css/syntax_highlight.css',
						filters = 'yui_css', output = 'css/gen/packed.sh.css')
register('css_sh', css_sh_bundle)

css_sh_bundle = Bundle('css/diff_view.css',
						filters = 'yui_css', output = 'css/gen/packed.dv.css')
register('css_dv', css_sh_bundle)

css_markitup_bundle = Bundle('markitup/skins/simple/style.css',
							 'markitup/sets/markdown/style.css',
						filters = 'yui_css', output = 'css/gen/packed.markitup.css')
register('css_markitup', css_markitup_bundle)

### JavaScript ###
js_core_bundle = Bundle('js/jquery.dajax.core.js',
						'js/jquery.notifyBar.js',
						'js/jquery.autocomplete.js',
						'js/jquery.highlight.js',
						'js/jquery.rating.js',
						'js/jquery.tipTip.js',
						'js/jquery.boxy.js',
						'js/jquery.history.js',
						'js/jquery.tag.editor.js',
						filters = 'yui_js', output = 'js/gen/packed.core.js')
register('js_core', js_core_bundle)

js_markitup_bundle = Bundle('markitup/jquery.markitup.js',
							'markitup/sets/markdown/set.js',
						filters = 'jsmin', output = 'js/gen/packed.markitup.js')
register('js_markitup', js_markitup_bundle)

js_graphael_bundle = Bundle('js/graphael/raphael.js',
							'js/graphael/g.raphael.js',
							'js/graphael/g.pie.js',
							'js/graphael/g.bar.js',
							'js/graphael/g.line.js',
						filters = 'jsmin', output = 'js/gen/packed.graphael.js')
register('js_graphael', js_graphael_bundle)