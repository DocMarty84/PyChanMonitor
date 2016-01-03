var app = {
    // Application Constructor
    initialize: function() {
        // "hidden" class is added by default to avoid displaying the alerts at page loading
        $("#fail").removeClass("hidden").hide();
        $("#success").removeClass("hidden").hide();
        this.bindEvents();
    },

    // Bind Event Listeners
    bindEvents: function() {
        var self = this;
        $("#monitor").submit(function(ev) {
            self.onSubmitMonitor(ev);
        });
        $("#monitor_json").submit(function(ev) {
            self.onSubmitMonitorJson(ev);
        });
        $(".close").click(function(ev) {
            $("#fail").hide();
            $("#success").hide();
        });
    },

    showAlert: function(p) {
        if (p.error || !p.result) {
            $("#success").hide();
            $('#fail').fadeIn('fast').delay(2000).queue(function() {
                $(this).fadeOut('slow').dequeue();
            });
        } else {
            $("#url").val('');
            $("#fail").hide();
            $('#success').fadeIn('fast').delay(2000).queue(function() {
                $(this).fadeOut('slow').dequeue();
            });
        }
    },

    onSubmitMonitorJson: function(ev) {
        ev.preventDefault();
        var self = this;
        var data = {};
        data.id = 1;
        data.jsonrpc = "2.0";
        data.method = "App.add_url_json";
        data.params = {}
        data.params.url = $("#url").val();
        data.params.password = $("#password").val();
        server_endpoint = "/add_url_json"

        var req = {
            url: server_endpoint,
            type: "POST",
            headers: {"Content-Type": "application/json"},
            data: JSON.stringify(data),
            dataType: "json",
        }
        $.ajax(req).then(function(p) {
            self.showAlert(p);
        });
    },

    onSubmitMonitor: function(ev) {
        ev.preventDefault();
        var self = this;
        var data = {};
        data.url = $("#url").val();
        data.password = $("#password").val();
        var server_endpoint = "/add_url";

        $.post(server_endpoint, data).then(function(p) {
            self.showAlert(p);
        });
    },

};

app.initialize();
