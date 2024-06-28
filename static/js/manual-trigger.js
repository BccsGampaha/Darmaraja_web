/*
	--------------------------------
	Infinite Scroll Behavior
	Manual / Twitter-style
	--------------------------------
	
	
*/

(function($, undefined) {
	$.extend($.infinitescroll.prototype,{

		_setup_twitter: function infscr_setup_twitter () {
			var opts = this.options,
				instance = this;

			// Bind nextSelector link to retrieve
			$(opts.nextSelector).click(function(e) {
				if (e.which == 1 && !e.metaKey && !e.shiftKey) {
					e.preventDefault();
					instance.retrieve();
				}
			});

			// Define loadingStart to never hide pager
			instance.options.loading.start = function (opts) {
				opts.loading.msg
					.appendTo(opts.loading.selector)
					.show(opts.loading.speed, function () {
						instance.beginAjax(opts);
					});
			}
		},
		_showdonemsg_twitter: function infscr_showdonemsg_twitter () {
			var opts = this.options,
				instance = this;

			//Do all the usual stuff
			opts.loading.msg
				.find('img')
				.hide()
				.parent()
				.find('div').html(opts.loading.finishedMsg).animate({ opacity: 1 }, 2000, function () {
					$(this).parent().fadeOut('normal');
				});

			//And also hide the navSelector
			$(opts.navSelector).fadeOut('normal');

			// user provided callback when done
			opts.errorCallback.call($(opts.contentSelector)[0],'done');

		}

	});
})(jQuery);
