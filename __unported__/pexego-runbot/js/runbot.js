(function() {

  $(function() {
    $('.dropdown-toggle').dropdown();
    return $('.pane td').mouseover(function() {
      return $(this).find('.action-toggle').show();
    }).mouseout(function() {
      return $(this).find('.action-toggle').hide();
    });
  });

}).call(this);
