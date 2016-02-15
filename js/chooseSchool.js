
var currentState = undefined;
var currentIncome = undefined;

// Closes the Responsive Menu on Menu Item Click
$('.btn-income').click(function() {
  currentIncome = $(this).attr('inc');
  $('.btn-income').removeClass('active');
  $(this).addClass('active');
  makeHrefLink();
})

$('.btn-state').click(function() {
  currentState = this.innerHTML;
  if (currentState == 'Show All') {
      currentState = 'None';
  }
  $('.btn-state').removeClass('active');
  $(this).addClass('active');
  makeHrefLink();
});

function makeHrefLink() {
    var linkHref = "#files";
    var linkName = "Choose Income and State";
    var $gb = $('#goBtn');
    if (currentState === undefined) {
        linkName = "Choose your State/Territory";
        $gb.removeClass('active');
    } else if (currentIncome === undefined) {
        linkName = "Choose your Income";
        $gb.removeClass('active');
    } else {
        linkName = "View College Costs!";
        linkHref = "data/2016_" + currentState + currentIncome + ".html";
        $gb.addClass('active');
    }
    $gb.html(linkName).attr('href', linkHref);
}

$('.btn-showCost').click(function() {
    var $this = $(this);
    var thisId = $this.attr('id');
    console.log(thisId);
    var $pre = $('#pre' + thisId);
    console.log($pre);
    $pre.css('display', 'block');
    $this.css('display', 'none');
  });
