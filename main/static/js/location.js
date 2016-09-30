

$("#date_debut").blur(function() {

    if(isDate($(this).val())){
        var currVal = $(this).val();
        var rxDatePattern = /^(\d{1,2})(\/|-)(\d{1,2})(\/|-)(\d{4})$/; //Declare Regex
        var dtArray = currVal.match(rxDatePattern); // is format OK?

        if (dtArray == null)
            return false;

        //Checks for mm/dd/yyyy format.
        dtDay = dtArray[1];
        dtMonth= dtArray[3];
        dtYear = dtArray[5];

        var result_plus_one = new Date(dtYear, dtMonth, dtDay);
        var result = new Date(dtYear, dtMonth, dtDay);

        result_plus_one.setDate(result_plus_one.getDate() + 365);
        var dd = result_plus_one.getDate();
        var mm = result_plus_one.getMonth();
        var y = result_plus_one.getFullYear();

        /*var someFormattedDate = dd + '/'+ mm + '/'+ y;
        $('#date_fin').val(someFormattedDate);

        result.setDate(result.getDate() + 355);

        dd = result.getDate();
        mm = result.getMonth();
        y = result.getFullYear();

        someFormattedDate = dd + '/'+ mm + '/'+ y;
        $('#renonciation').val(someFormattedDate);*/

    }
});

    function isDate(txtDate){
        var currVal = txtDate;
        if(currVal == '')
            return false;

        var rxDatePattern = /^(\d{1,2})(\/|-)(\d{1,2})(\/|-)(\d{4})$/; //Declare Regex
        var dtArray = currVal.match(rxDatePattern); // is format OK?

        if (dtArray == null)
            return false;

        //Checks for mm/dd/yyyy format.
        dtDay = dtArray[1];
        dtMonth= dtArray[3];
        dtYear = dtArray[5];

        if (dtMonth < 1 || dtMonth > 12) {
            return false;
        } else if (dtDay < 1 || dtDay> 31) {
            return false;
        } else if ((dtMonth==4 || dtMonth==6 || dtMonth==9 || dtMonth==11) && dtDay ==31) {
            return false;
        } else if (dtMonth == 2) {
            var isleap = (dtYear % 4 == 0 && (dtYear % 100 != 0 || dtYear % 400 == 0));
            if (dtDay> 29 || (dtDay ==29 && !isleap)) {
                return false;
            }
        }
        if (dtYear< 1900){
            return false;
        }
        return true;
    }

    $("#bt_save_new_assurance").click(function(event) {
        event.preventDefault();
        var target = $(event.target);
        var id = target.attr("id");
        var form = target.form;
        var description = $("#txt_description_assurance_other").val();
        var name = $("#txt_nom_assurance_other").val();
        var data = new FormData();
        data.append('description', description);
        data.append('nom', name);
        var loc = location.href;
        var url = "{% url 'assurance_create' %}";
        url = "http://127.0.0.1:8000/assurance_create/";
        $.ajax({
            url: url,
            type: 'POST',
            data : data,
            processData: false,
            contentType: false,
            complete: function(xhr, statusText){
                if(xhr.status=='0'){
                    //problem occured

                }else{
                    $('#slt_assurances').append('<option val="1" selected>'+name+'</option>');
                }

            }

        });

    });

    $("#bt_prolongation_submit").click(function(event) {
        event.preventDefault();
        var id_location = $("#id_location_prolongation").val();
        var type_prolongation = $( "#slt_type_prolongation option:selected" ).val();
        if (type_prolongation=='1'){
            $.ajax({

                url: "/prolongation?id_location=" + id_location + "&type_prolongation="+type_prolongation,
                processData: false,
                complete: function(xhr, statusText){
                    if(xhr.status=='0'){
                        //problem occured

                    }else{
                        /*$.ajax({
                            url: "/location/prepare/update/all/" + id_location,

                        });*/
                    }

            }
            });
        }
    });
    $("#bt_prolongation").click(function(event) {
        $("#txt_msg_error_slt_type_prolongation" ).html('');
        $("#txt_msg_error_slt_type_prolongation").css('visibility', 'hidden').css('display','none');
        if ($( "#slt_type_prolongation").prop('selectedIndex') <= 0 ){
            $("#txt_msg_error_slt_type_prolongation").html('Faut sélectionner une durée de prolongation');
            $("#txt_msg_error_slt_type_prolongation").css('visibility', 'visible').css('display','block');
            return false;
        }
        return true;
    });
    $("#etat_suivi").click(function(event) {
        var etat = $("#etat_suivi option:selected" ).val();

        if(etat=='PAYE'){
            $("#txt_loyer_percu").val(parseFloat($("#spn_loyer_percu").html()));
        }
    });

    $("#bt_save_new_fonction").click(function(event) {

        event.preventDefault();
        var target = $(event.target);
        var id = target.attr("id");
        var form = target.form;

        var name = $("#txt_nom_fonction_other").val();
        var data = new FormData();
        data.append('nom', name);
        var loc = location.href;
        var url = "{% url 'assurance_create' %}";
        url = "http://127.0.0.1:8000/fonction_create/?nom="+name;
        $.ajax({
            url: url,
            type: 'GET',
            processData: false,
            success: function(data){
            console.log(data);
                alert('i'+data.id);
                $('#slt_profession').append('<option val="1" selected>'+name+'</option>');
            },


        });

    });
    $("#btn_clean_personnes").click(function(event) {
        $("#nom").val('');
        $("#prenom").val('');
    });




