// Generated by CoffeeScript 1.8.0
$(document).ready(function() {
  $("#imagelisting").on("click", ".imagedetailblock .edittoggle", function() {
    var id;
    $(this).closest(".imagedetails").hide();
    id = $(this).data("image-id");
    return $("#imageform-" + id).show();
  });
  $("#imagelisting").on("click", ".imagedetailblock .canceltoggle", function() {
    var id;
    $(this).closest(".imagedetailform").hide();
    id = $(this).data("image-id");
    return $("#details-" + id).show();
  });
  return $("#imagelisting").on("submit", ".imagedetailform", function() {
    var id, url;
    event.preventDefault();
    id = $(this).data("image-id");
    url = $(this).attr("action");
    return $.ajax({
      type: "post",
      url: url,
      data: $(this).serialize(),
      contentType: "application/x-www-form-urlencoded",
      success: function(data) {
        $("#block-" + id).replaceWith($(data.html));
        $("#imageform-" + id).hide();
        return $("#details-" + id).show();
      },
      error: function() {
        return alert("an error occurred, please try again later");
      }
    });
  });
});