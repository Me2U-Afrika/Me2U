function preparedDocument(){
    jQuery("form#search").submit(function(){
        text = jQuery("#id_q").val();
        text_length = jQuery("#id_q").val().length;


        if (text=="search" || text=="Search"){
            // pop up alert
            alert("Enter a search term");
            // halt submission of form
            return false
        }
         if (text_length < 3 ){
        // pop up alert
        alert("Search term should be atleast 3 characters long");
        // halt submission of form
        return false
        }
    });

//
//    jQuery("sumbitComment").click(addComment);
//
//
//    function addComment(){
//
//        var comment = {
//
//            comment: jQuery("#addComment").val()
//            id: jQuery("id_post").val()
//
//        };
//
//        jQuery.post("add/comment",comment,
//            function(response){
//
//            }
//        )
//
//    }


    jQuery("#submit_review").click(addProductReview);
    jQuery("#first_time").hide();
    jQuery("#first_time").click(slideToggleReviewForm);
    jQuery("#review_form").hide();
    jQuery("#add_review").click(slideToggleReviewForm);
    jQuery("#add_review").addClass('visible');
    jQuery("#cancel_review").click(slideToggleReviewForm);

    function slideToggleReviewForm(){
        jQuery("#add_review").slideToggle();
        jQuery("#review_form").slideToggle();
        jQuery("#first_time").slideToggle();


    };

    // toggles visibility of "write review" link
    // and the review form.

    function addProductReview(){
           console.log('we came here')


    // build an object of review data to submit

        var review = {
            title: jQuery("#id_title").val(),
            content: jQuery("#id_content").val(),
            rating: jQuery("#id_rating").val(),
            slug: jQuery("#id_slug").val(),
            country: jQuery("#id_country").val()
        };
        console.log(review)


        jQuery.post("add/review/", review,
          function (response){
            console.log("we got the response here")
            console.log(response)

            jQuery("#review_errors").empty();
            // evaluate the successs parameter
            if(response.success == "True"){
                  console.log('success for sure is True')

                  // disable the submit button to prevent duplicates
                  jQuery("#submit_review").attr('disabled','disabled');
                  // if this is first review, get rid of "no reviews" text
                  jQuery("#no_reviews").empty()
                  // add a new review section
                  jQuery("#reviews").prepend(response.html).slideDown();
                  // Get response and style interval
                  new_review = jQuery("#reviews").children(":first");

                  new_review.addClass('new_review');
                  // hide the review review_form
                  jQuery("#review_form").slideToggle();
            }
            else{
                //console.log('we might as well end here')
                // add the error text to the review_errors div
                  jQuery("#review_errors").append(response.html);
                }
          }, "json");
    }

    // CONTACT SELLER
    // jQuery("#contact_seller").click(slideToggleSellerContact);
    // jQuery("#seller_contact").hide();
    //
    //
    // function slideToggleSellerContact(){
    //     jQuery("#seller_contact").slideToggle();
    //
    // }

    jQuery("#edit-option").click(slideToggleEditOptions);
    jQuery("#hideable-edit-options").hide();


    function slideToggleEditOptions(){
        jQuery("#hideable-edit-options").slideToggle();

    }


//    PRODUCT TAGS
    jQuery("#tag_product").click(slideToggleAddTag);
    jQuery("#add_tag").hide();
    jQuery("#id_tag").hide();
    jQuery("#add_tag").click(addTag);

    function slideToggleAddTag(){
        jQuery("#add_tag").slideToggle();
        jQuery("#id_tag").slideToggle();
    }

    jQuery("#id_tag").keypress(function(event){
        //  Key code 13 corresponds to the Enter key on a user’s keyboard.
        if (event.keypress == Enter && jQuery("#id_tag").val().length > 2){
            addTag()
            event.preventDefault();
        }
    });

    function addTag(){
        console.log('here I am to add some tags')
        var tag = {tag: jQuery("#id_tag").val(),
               slug: jQuery("#id_slug").val()
               }

         console.log(tag)

        jQuery.post("add/tag/", tag,
            function(response){

                console.log('I got some response as well from view')

                if(response.success == 'True'){
                    jQuery("#add_tag").hide();
                    jQuery("#id_tag").hide();
                     jQuery("#no_tags").empty()
                  // add a new review section
                    jQuery("#tags").append(response.html).slideDown();
                    new_review = jQuery("#tags").children(":first");

                    new_review.addClass('new_review');
                    jQuery("#id_tag").val("");
                }
            }, "json");
    }

    var token =  jQuery('input[name="csrfmiddlewaretoken"]').attr('value')

    function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", token);
            }
        }
    });


// Checkout form code
    var hideable_billing_form = $('.hideable_billing_form');
    var hideable_shipping_form = $('.hideable_shipping_form');
    var same_as_shipping = $('.same_as_shipping')
    var hideable_form = $('.hideable_form')


    var use_default_shipping = document.querySelector("input[name='use_default_shipping']");
    var add_new_shipping = document.querySelector("input[name='add_new_shipping']");
    var use_default_billing = document.querySelector("input[name='use_default_billing']");


    var form = document.getElementById('same_billing_address');
    form.addEventListener('change', function(event){
      event.preventDefault();

      if (form.checked) {
          same_as_shipping.hide();
        } else {
          same_as_shipping.show();

        };
    });

    add_new_shipping.addEventListener('change', function(event) {
      event.preventDefault();

        if (add_new_shipping.checked) {
          hideable_form.hide();
        } else {
          hideable_form.show();


        };
    });


    use_default_shipping.addEventListener('change', function(event) {
      event.preventDefault();

        if (use_default_shipping.checked) {
          hideable_shipping_form.hide();
        } else {
          hideable_shipping_form.show();
        };
    });

    // var form = document.getElementById('use_default_billing');
    // form.addEventListener('change', function(event) {

    use_default_billing.addEventListener('change', function(event) {
      event.preventDefault();

        if (use_default_billing.checked) {
          hideable_billing_form.hide();
        } else {
          hideable_billing_form.show();
        };
    });

}

jQuery(document).ready(preparedDocument)
//statusBox()
