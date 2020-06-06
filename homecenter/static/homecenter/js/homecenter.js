$(document).ready(function () {
    // Actuelle client page
    let page = $(location).attr('pathname').split('/')[2];

    //************ Socket io client listner ***********************************/
    //let socket = io.connect('http://0.0.0.0:8001');
    let socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
    console.log(window.location.protocol + '//' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log('Le client socketio est connecté');
        console.log(socket.id);
    });

    socket.on('disconnect', function () {
        console.log("Le client socketio s'est déconnecté");
        console.log(socket.id);
    });

    socket.on('update light state', function (msg) {
        let lightNode = msg.data['value_id'];
        let lightSwitch = $('#' + lightNode).parent().parent().find('#light_switch');
        let lightIcon = lightSwitch.parent().parent().parent().find('#light_icon');
        let lightStateElement = lightSwitch.parent().parent().find('.light_state');
        let nodeState = 0;
        if (msg.data['data'] === false) {
            nodeState = "Off";
        } else if (msg.data['data'] === true) {
            nodeState = "On";
        }
        setSwitchPosition(lightSwitch, nodeState);
        changeElementClass($(lightIcon), nodeState, "mdi-yellow");
        $(lightStateElement).text(nodeState);
    });

    socket.on('update roller shutter state', function (msg) {
        let newLevel;
        if (msg.data['data'] === 99) {
            newLevel = "100";
        } else {
            newLevel = msg.data['data'];
        }
        let RSValueId = msg.data['value_id'];
        let rsNodeElement = $('#' + RSValueId);
        let levelElement = rsNodeElement.parent().find('#level-value');
        levelElement.text(newLevel);
    });

    let counter = 0;
    socket.on('update roller shutter power state', function (msg) {
        //console.log('Action sur le noeud : '+ msg.data['node_id'] + '\n' + 'Power : '+ msg.data['data'] + msg.data['units'] );
        let node_id = msg.data['node_id'];
        let nodeElement = $('#' + msg.data['node_id']);
        let power = msg.data['data'];
        let units = msg.data['units'];
        // console.log("Power est à "+power+" "+units);
        if ((page === "roller_shutter") && (power === 0.0)) {
            setTimeout(function () {
                nodeElement.find("#input")[0].value = '0';
                nodeElement.find("#range-value").text('0');
            }, 3000)
        }
    });

    socket.on('network data', function (msg) {
        let homeId = msg.data['home_id'][0];
        let networkState = msg.data['state'][0];
        let networkStringState = msg.data['state_str'][0];
        let networkNodeCount = msg.data['count'];
        let networkSwitchElement = $('#network_switch');
        let networkInputElement = $('#nw_input');


        console.log("Données réseau : " + msg['data'])
        console.log('Home id : ' + msg.data['home_id'] + '\n' + 'Etat du réseau : ' +
            msg.data['state_str'] + '\n' + 'Nombre de noeuds : ' + msg.data['count']);
        if (networkStringState === 'Network ready') {
            setSwitchPosition(networkSwitchElement, 'On');
            $('#nw_text_state').replaceWith('<i id="nw_text_state">Le réseau est démarré !</i>');
            networkInputElement.val('On');
        } else if (networkStringState === 'Network is stopped') {
            setSwitchPosition(networkSwitchElement, 'Off');
            $('#nw_text_state').replaceWith('<i id="nw_text_state">Le réseau est arrêté !</i>');
            networkInputElement.val('Off');
        } else {
            console.log('Problème de condition de boucle');
        }

    });

    /***************** Collapse the nemu bar **********************************/
    let content = $('#content');
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    $(content).on('click', function () {
        $('#sidebar').removeClass('active');
    });

    let home_menu = $('#home');
    let config_menu = $('#config');

    $(home_menu).parent().find('a').on('click', function () {
        $(config_menu).removeClass('show');
    });

    $(config_menu).parent().find('a').on('click', function () {
        $(home_menu).removeClass('show');
    });

    /******** Repositionning wrapper, messages texts and content  *************/
    function repositionne() {
        let headerHeight = Math.round($('#header').height());
        $('.wrapper').css('top', headerHeight + 5 + "px");
        $('#messages').css('top', headerHeight + 5 + "px");
        $(content).css('top', headerHeight + 5 + "px");
    }

    $(window).on("resize", function () {
        repositionne();
    });

    window.onload = repositionne();

    /********* Function to hide messages after time ***************************/
    function message_hide(timeout) {
        setTimeout("$('.message').fadeOut(500);", timeout);
        if ($('.message').hasClass("alert-info")) {
            setTimeout("$('.message').empty()", timeout);
        }
    }

    /******** Function to blinking the warning messages ***********************/
    function blink_message_warning() {
        let warning = $('.message.alert-warning');
        warning.fadeOut(500);
        warning.fadeIn(500);
    }

    setInterval(blink_message_warning, 1500);

    /***** Function to set the network switch position ************************/
    function setSwitchPosition(element, state) {
        if (state === "On" && element.hasClass("fa-rotate-180")) {
            element.removeClass("fa-rotate-180");
        } else if (state === "Off" && !element.hasClass("fa-rotate-180")) {
            element.addClass("fa-rotate-180");
        }
        return state;
    }

    /*** Function to add property to class with condition "On" or "Off" *******/
    function changeElementClass(element, state, property) {
        if (state === "On" && !element.hasClass(property)) {
            element.addClass(property);
        } else if (state === "Off" && element.hasClass(property)) {
            element.removeClass(property);
        }
        return state;
    }

    //*********** Function that display client messages ***********************/
    function displayResponseMessage(data) {
        if (data['messages']['warning']) {
            $('.message').replaceWith('<p class="message text-center offset-2 col-8 rounded alert alert-warning">' +
                data['messages']['warning'] + '</p>');
        } else if (data['messages']['success']) {
            $('.message').replaceWith('<p class="message text-center offset-2 col-8 rounded alert alert-info">' +
                data['messages']['success'] + '</p>');
        } else if (data['messages']['error']) {
            $('.message').replaceWith('<p class="message text-center offset-2 col-8 rounded alert alert-danger">' +
                data['messages']['error'] + '</p>');
        }
        message_hide(1000);
    }

    if (!$('.message').hasClass("alert-danger")) {
        message_hide(1500);
    } else if ($('.message').hasClass("alert-danger")) {
        message_hide(3000);
    }

    //load state and set switch position if page is "network"
    console.log(page);
    if (page === "network") {
        // Define variable global
        window.state = $('#nw_input')[0].value;
        // Set the right switch position
        setSwitchPosition($("#network_switch"), state);
    }

    /***** Set the session tocken before POST with AJAX ***********************/
    let csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();

    /**** Network start.stop Switches click change and POST the state *********/
    $('#network_switch').on('click', function () {
        if ($('#nw_input')[0].value === "On") {
            state = "Off";
            $('.message').replaceWith("<p class='message offset-2 col-8 rounded alert alert-warning'>" +
                "Le réseau est en cours d'arrêt. Veuillez patienter !</p>");
        } else {
            state = "On";
            $('.message').replaceWith("<p class='message offset-2 col-8 rounded alert alert-warning'>" +
                "Le réseau est en cours de démarrage. Veuillez patienter !</p>");
        }
        setSwitchPosition($(this), state);

        let data = {
            'state': state,
        };

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: '',
            dataType: "json",
            traditional: true,
            data: data,
            success: function (data) {
                displayResponseMessage(data);
                $('#nw_text_state').replaceWith('<i id="nw_text_state">Le réseau est ' + data.nw_text_state + '</i>');
            }
        });
    });

    /************* Rollershutters commands ************************************/
    let setLevel = 0;
    let direction = 0;
    $('.rs-shutter').click(function () {
        if ($(this).css('color') !== 'rgb(128, 128, 128)') {
            let stop = 0;
            let nodeId = $(this).parent().parent().parent().parent().attr('id');
            let nodeInstance = $(this).parent().parent().attr('rs_instance');
            let slider = $(this).parent().parent().find("#input");
            let rangeValue = $(this).parent().parent().find("#range-value");
            let rangeLevel = parseInt(slider[0].value);
            // let nwState = $('.nw_state').value;
            //let slider = $(this).parent().parent().parent().parent().find("#input")
            let level = $('#level').attr('id');
            if (($(this).attr('id') === 'btn_close') && (rangeLevel <= 0)) {
                direction = 0;
                setLevel = 0;
            }
            else if (($(this).attr('id') === 'btn_open') && (rangeLevel <= 0)) {
                direction = 1;
                setLevel = 99;
            }
            else if (($(this).attr('id') === 'btn_stop') && (rangeLevel <= 0)) {
                stop = 1;
            }
            else if (rangeLevel > 0) {
                setLevel = rangeLevel;
            }

            let data = {
                'node_id': nodeId,
                'node_instance': nodeInstance,
                'setLevel': setLevel,
                'level': level,
                'stop': stop,
                'direction': direction,
            };

            $.ajax({
                type: "POST",
                headers: {'X-CSRFToken': csrf_token},
                url: "",
                dataType: "json",
                traditional: true,
                data: data,
                success: function (data) {
                    displayResponseMessage(data);
                }
            });
        }
    });

    // Activate/deactivate button when roller shutter total opened or closed **/
    function change_btn_state(nodeInstanceLevelElement) {
        let nodeInstanceLevelValue = nodeInstanceLevelElement.text();
        let btnOpen = nodeInstanceLevelElement.parent().parent().find('#btn_open');
        let btnClose = nodeInstanceLevelElement.parent().parent().find('#btn_close');
        if (nodeInstanceLevelValue === '0') {
            btnClose.css('color', "grey");
        } else if (nodeInstanceLevelValue !== '0') {
            btnClose.css("color", "black");
        }

        if (nodeInstanceLevelValue === '100') {
            btnOpen.css("color", "grey");
        } else if (nodeInstanceLevelValue !== '100') {
            btnOpen.css("color", "black");
        }
    }

    $("body").on('DOMSubtreeModified', '#level-value', function () {
        change_btn_state($(this));
    });

    $('.level-value').each(function () {
        change_btn_state($(this));
    })

    /********Rollershutters range slider **************************************/
    $('.card').each(function (i) {
        let slider = $(this).find('#input')[0];
        if (slider !== undefined) {
            let rangeLevel = slider.value;
            let output = $(this).find('#range-value')[0];
            output.innerHTML = rangeLevel; // Display the default slider value
            // Update the current slider value (each time you drag the slider handle)
            slider.oninput = function () {
                output.innerHTML = this.value;
            };
        }

        /****** Init light state when web page is reloaded ********/
        let light_icon = $(this).find('#light_icon');
        let light_switch = $(this).find('#light_switch');
        let init_state = $(this).find('.light_state').text();
        setSwitchPosition($(light_switch), init_state);
        changeElementClass($(light_icon), init_state, "mdi-yellow");

    });


    /************** Nodes configurations **************************************/
    $('.input_name, .input_location').keypress(function (event) {
        let key = event.which || event.keyCode;
        if (key === 13) {
            let nodeId = $(this).parent().parent().parent().find('#node_id').text().trim();
            let nodeInstance = $(this).parent().parent().parent().find('#instance_id').text().trim();
            let nodeName = $(this).parent().parent().parent().find('#input_name')[0].value;
            let nodeLocation = $(this).parent().parent().parent().find('#input_location')[0].value;

            let data = {
                'node_id': nodeId,
                'node_instance': nodeInstance,
                'name': nodeName,
                'location': nodeLocation
            };

            $.ajax({
                type: "POST",
                headers: {'X-CSRFToken': csrf_token},
                url: "",
                dataType: "json",
                traditional: true,
                data: data,
                success: function (data) {
                    displayResponseMessage(data);
                }
            });
        }
    });

    //******** Roller shutter Calibration button *******/
    $('.BtnCalibrate').click(function () {
        let nodeId = parseInt($(this).parent().parent().parent().find("#node_id").text().trim());
        let calibrate = 'True';
        $(this).prop('disabled', true);
        $(this).css('background-color', 'red');
        //$(this).attr('disabled', true);

        let data = {
            'node_id': nodeId,
            "calibrate": calibrate
        };

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: "",
            dataType: "json",
            traditional: true,
            data: data,
            success: function (data) {
                displayResponseMessage(data);
            }
        })
    });

    $('.switch_type').on('change', function(){
        let nodeId = parseInt($(this).parent().parent().parent().find("#node_id").text().trim());
        let typeSwitchValue = $(this).val();
        let data = {
            'node_id': nodeId,
            'type_switch_value': typeSwitchValue
        };

        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: "",
            dataType: "json",
            traditional: true,
            data: data,
            success: function (data) {
                displayResponseMessage(data);
            }
        })

    });

    /******************** Lights commands *************************************/
    function update_light_node(light_instance, setState) {

        let string_light_instance = light_instance.toString();
        let lightInstanceElement = $('#' + string_light_instance + '');
        let nodeId = lightInstanceElement.parent().parent().parent().parent().attr('id');
        let nodeInstanceId = light_instance.toString();
        let lightSwitch = lightInstanceElement.parent().parent().find('#light_switch');
        setSwitchPosition($(lightSwitch), setState);
        let data = {
            'nodeId': nodeId,
            'nodeInstance': nodeInstanceId,
            'setState': setState
        };
        let lightStateElement = lightInstanceElement.parent().parent().find('.light_state');
        let lightIcon = lightInstanceElement.parent().parent().parent().find('#light_icon');
        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: "",
            dataType: "json",
            traditional: true,
            data: data,
            success: function (data) {
                $(lightStateElement).text(data.state);
                //$(setStateElement)[0].value = (data.state);
                $(lightStateElement)[0].value = (data.state);
                changeElementClass($(lightIcon), data.state, "mdi-yellow");
                displayResponseMessage(data);
                if (data.nw_state === 'Off') {
                    setSwitchPosition($(lightSwitch), data.nw_state);
                }
            }
        });
    }

    let light_switch = $('.light_switch');
    $(light_switch).click(function () {
        let light_instance = $(this).parent().parent().find('.light_instance').attr('id');
        let setState = $(this).parent().parent().find('.light_state').text();
        if (setState === 'Off') {
            setState = 'On';
        } else {
            setState = 'Off';
        }
        update_light_node(light_instance, setState);
    });

    /****************  User administation commands ****************************/
    let userDeleteBtn = $('.userDeleteBtn');

    $(userDeleteBtn).click(function () {
        let userId = $(this).attr('id');
        let data = {
            'user_id': userId,
            'action': 'UserDelete'
        };
        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': csrf_token},
            url: "",
            dataType: "json",
            traditional: true,
            data: data,
            beforeSend: function () {
                return confirm("Etes-vous sûr de vouloir supprimer l'utilisateur");
            },
            success: function (data) {
                displayResponseMessage(data);
                if (data['messages']['success']) {
                    $('tr#' + userId).remove()
                }
            }
        });
    });

});
