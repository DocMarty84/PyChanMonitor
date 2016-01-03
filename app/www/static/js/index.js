var app = {
    // Application Constructor
    initialize: function() {
        // "hidden" class is added by default to avoid displaying the alerts at page loading
        $(".alert").removeClass("hidden").hide();
        this.bindEvents();
    },

    // Bind Event Listeners
    bindEvents: function() {
        document.addEventListener('deviceready', function() {
            app.getURL('deviceready');
        }, false);
        $(".close").click(function(ev) {
            $(".alert").hide();
        });
    },

    showAlert: function(p) {
        if (p.no_url) {
            $("#fail").hide();
            $("#success").hide();
            $('#no_url').fadeIn('fast').delay(4000).queue(function() {
                $(this).fadeOut('slow').dequeue();
            });
        } else if (p.error || !p.result) {
            $("#no_url").hide();
            $("#success").hide();
            $('#fail').fadeIn('fast').delay(4000).queue(function() {
                $(this).fadeOut('slow').dequeue();
            });
        } else {
            $("#fail").hide();
            $("#no_url").hide();
            $('#success').fadeIn('fast').delay(4000).queue(function() {
                $(this).fadeOut('slow').dequeue();
            });
        }
    },

    getURL: function(ev) {
        var self = this;

        window.plugins.webintent.getExtra(window.plugins.webintent.EXTRA_TEXT,
            function(url) {
                self.monitor(url)
            }, function() {
                var p = {};
                p.no_url = true;
                self.showAlert(p);
            }
        );
    },

    monitor: function(url) {
        var self = this;
        var data = {};
        data.url = url;
        data.password = $("#password").val();
        var server_endpoint = $("#server_endpoint").val();

        $.post(server_endpoint, data).then(function(p) {
            self.showAlert(p);
        });
    },

};

app.initialize();
