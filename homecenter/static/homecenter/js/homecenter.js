$(document).ready(function () {
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

    /****************************** Repositionning wrapper, messages texts and content  ****************/
    function repositionne() {
        let headerHeight = Math.round($('#header').height());
        $('.wrapper').css('top', headerHeight + 5 + "px");
        $('#messages').css('top', headerHeight + 5 + "px");
        $(content).css('top', headerHeight + 5 + "px");
    }

    $(window).on("resize", function() {
        repositionne();
    });

    window.onload = repositionne();

    /************************* Function to hide messages after time *************************************/
    function message_hide(timeout){
        setTimeout( "$('.message').fadeOut(500);", timeout);
        if ($('.message').hasClass("alert-info")){
            setTimeout("$('.message').empty()",timeout);
        }
    }

    /************************ Function to blinking the warning messages **********************************/
    function blink_message_warning() {
        let warning = $('.message.alert-warning');
        warning.fadeOut(500);
        warning.fadeIn(500);
    }
    setInterval(blink_message_warning, 1000);

    /********************************** Function to set the switch position *****************************/
    function setSwitchPosition (element, state){
        if (state==="On" && element.hasClass("fa-rotate-180")) {
            element.removeClass("fa-rotate-180");
        }
        else if (state==="Off" && !element.hasClass("fa-rotate-180")){
            element.addClass("fa-rotate-180");
        }
        return state;
    }

    /************************** Function to add property to class with condition "On" or "Off" *************/
    function changeElementClass (element, state, property){
        if (state==="On" && !element.hasClass(property)) {
            element.addClass(property);
        }
        else if (state==="Off" && element.hasClass(property)){
            element.removeClass(property);
        }
        return state;
    }

    function displayResponseMessage (data){
        if (data['messages']['warning']) {
            $('.message').replaceWith('<p class="message text-center offset-2 col-8 rounded alert alert-warning">' +
                data['messages']['warning'] + '</p>');
        }
        else if (data['messages']['success']){
            $('.message').replaceWith('<p class="message text-center offset-2 col-8 rounded alert alert-info">' +
                data['messages']['success'] + '</p>');
        }
        else if (data['messages']['error']){
            $('.message').replaceWith('<p class="message text-center offset-2 col-8 rounded alert alert-danger">' +
                data['messages']['error'] + '</p>');
        }
        message_hide(1000);
    }

    if (!$('.message').hasClass("alert-danger")){
        message_hide(1500);
    }
    else if ($('.message').hasClass("alert-danger")){
        message_hide(3000);
    }

    //load state and set switch position if page is "network"
    let page = $(location).attr('pathname').split('/')[2];
    console.log(page);
    if (page === "network"){
        // Define variable global
        window.state = $('#nw_input')[0].value;
        // Set the right switch position
        setSwitchPosition($(".switch"), state);

        console.log(state);
    }

    /************************* Set the session tocken before POST with AJAX *************************************/
    let csrf_token = jQuery("[name=csrfmiddlewaretoken]").val();

    /*************************** Switches click change and POST the state *******************************************/
    $('.switch').on('click', function(){
        if (state ==="On"){
            state = "Off";
            $('.message').replaceWith("<p class='message offset-2 col-8 rounded alert alert-warning'>" +
                "Le réseau est en cours d'arrêt. Veuillez patienter !</p>");
        }
        else {
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
            headers: {'X-CSRFToken': csrf_token },
            url: '',
            dataType: "json",
            traditional: true,
            data: data,
            success: function(data) {
                   displayResponseMessage(data);
                   $('#nw_text_state').replaceWith('<i id="nw_text_state">Le réseau est '+data.nw_text_state+'</i>');
            }
        });
    });

    /************************************* Rollershutters commands *****************************************/
    // Set the rollershutter level
    let setLevel =0;
    $('.rs-shutter').click(function() {
        let stop = 0;
        let nodeId = $(this).parent().parent().parent().parent().attr('id');
        let nodeInstance = $(this).parent().parent().attr('rs_instance');
        let rangeLevel = parseInt($(this).parent().parent().parent().parent().find( "#input")[0].value);
        let nwState = $('.nw_state').value;
        let level= $('#level').attr('id');

        if (($(this).attr('id') === 'btn_close') && (rangeLevel <= 0)) {
            setLevel = 0;
        }
        else if (($(this).attr('id') === 'btn_open') && (rangeLevel <= 0)) {
            setLevel = 99;
        }
        else if (($(this).attr('id') === 'btn_stop')) {
            stop = 1;
        }
        else {
            setLevel = rangeLevel;
        }

        let data = {
            'node_id': nodeId,
            'node_instance': nodeInstance,
            'setLevel': setLevel,
            'level': level,
            'stop': stop
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
                console.log('message: '+data.messages, "Etat: "+data.node_state, "Niveau: "+data.level);
            }
        });
    });

    /************************** Rollershutters range slider ***********************************************/
    $('.card').each(function (i){
        let slider = $(this).find( '#input')[0];
        if (slider !== undefined) {
            let rangeLevel = slider.value;
            let output = $(this).find('#range-value')[0];
            output.innerHTML = rangeLevel; // Display the default slider value
            // Update the current slider value (each time you drag the slider handle)
            slider.oninput = function () {
                output.innerHTML = this.value;
            };
        }

        /****** Init light state web page reloaded ********/
        let light_icon = $(this).find('#light_icon');
        let light_switch = $(this).find('#light_switch');
        let init_state = $(this).find('.light_state').text();
        setSwitchPosition($(light_switch), init_state);
        changeElementClass($(light_icon), init_state, "mdi-yellow");

    });


});
