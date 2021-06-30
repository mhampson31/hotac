$(function() {
   $('#available .card-header').click(function() {
       /*$(this).parent().parent().find('.list-group-item-secondary').removeClass('list-group-item-secondary');
       var choices = $(this).next();
       setTimeout(function() {
           var maneuver = Math.floor(Math.random() * Math.floor(choices.children().length))
           choices.children().eq(maneuver).toggleClass('list-group-item-secondary');
       }, 250);*/
       var upgrade = $(this).attr('card_id');
       $('select').val(upgrade)
   });
});
