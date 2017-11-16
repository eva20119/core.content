$('.check_btn').on('click', function(e){
    $(this).siblings().toggle('normal')
    $(this).toggle('normal')
});

$('.send_btn').click(function (e) { 
    notify({
        type: "success", //alert | success | error | warning | info
        title: "訊息以進發佈程序，請勿多次發佈",
        position: {
            x: "right", //right | left | center
            y: "top" //top | bottom | center
        },
       
        size: "normal", //normal | full | small
        overlay: false, //true | false
        closeBtn: true, //true | false
        overflowHide: false, //true | false
        spacing: 20, //number px
        theme: "default", //default | dark-theme
        autoHide: true, //true | false
        delay: 3000, //number ms
        onShow: null, //function
        onClick: null, //function
        onHide: null, //function
        template: '<div class="notify"><div class="notify-text"></div></div>'
    });
});

$('#auto_release').change(function (e) { 
    $(this).siblings().toggle('normal')
});