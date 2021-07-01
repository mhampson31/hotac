$(function() {
   $('#available .card-header').click(function() {
       var upgrade = $(this).attr('card_id');
       $('select').val(upgrade)
   });
});
