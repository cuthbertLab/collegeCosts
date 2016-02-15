
var currentState = undefined;
var currentIncome = undefined;
var currentTest = '';
var currentTestClicked = false;

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

$('.btn-satact').click(function() {
    currentTest = this.innerHTML;
    if (currentTest == 'SAT') {
        currentTest = ''; // SAT was originally the default
    }
    $('.btn-satact').removeClass('active');
    $(this).addClass('active');
    currentTestClicked = true;
    makeHrefLink();
})


function makeHrefLink() {
    var linkHref = "#files";
    var linkName = "Choose Income and State";
    var $gb = $('#goBtn');
    if (currentIncome === undefined) {
        linkName = "Choose your Income";
        $gb.removeClass('active');
    } else if (currentState === undefined) {
        linkName = "Choose your State/Territory";
        // make the button do something anyhow now...
        linkHref = "data/2016_None" + currentIncome + currentTest + ".html";
        $gb.removeClass('active');
    } else {
        linkName = "View College Costs!";
        linkHref = "data/2016_" + currentState + currentIncome + currentTest + ".html";
        $gb.addClass('active');
    }
    $gb.html(linkName).attr('href', linkHref);
    if (currentIncome !== undefined && currentState !== undefined && currentTestClicked == true) {
        window.location.href = linkHref;
    }
    currentTestClicked = false;
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
