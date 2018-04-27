function createAndDownloadFile(fileName, content) {
    var aTag = document.createElement('a');
    var blob = new Blob([content]);
    aTag.download = fileName;
    aTag.href = URL.createObjectURL(blob);
    aTag.click();
    URL.revokeObjectURL(blob);
}

function downloadFile(fileName, url) {
    var aTag = document.createElement('a');
    aTag.download = fileName;
    aTag.href = url;
    aTag.click();
}

function changeImage(number){
	if (number > 12248) {
		document.getElementById("image").src = '/static/example.png';
	}else{
		document.getElementById("image").src = '/static/example_' + number + '.png';
	}
	
}

function showmore(){
  document.getElementById("filter_menu_showmore").style.display="block";
  document.getElementById("show_button").style.display="none";
  document.getElementById("filter_menu").style.height=460;
  document.getElementById("side_menu").style.top="10%";
}

function hide(){
  document.getElementById("filter_menu_showmore").style.display="none";
  document.getElementById("show_button").style.display="block";
  document.getElementById("filter_menu").style.height=195;
  document.getElementById("side_menu").style.top="20%";
}

function change_sunspot_type(){     
  var type = $("#sunspot_type").val();
  if (type == "magnetogram") {
    $("[name='attributes']").prop("checked",true); 
    $("[class='magnetogram']").removeAttr("disabled");
    $("[class='magnetogram']").prop("checked",true);
    $("[class='continuum']").prop("disabled",'disabled');
    $("[class='continuum']").removeAttr("checked");
  }
  else if (type == "continuum") {
    $("[name='attributes']").prop("checked",true); 
    $("[class='continuum']").removeAttr("disabled");
    $("[class='continuum']").prop("checked",true);
    $("[class='magnetogram']").prop("disabled",'disabled');
    $("[class='magnetogram']").removeAttr("checked");
  }
};

function change_plot_type()
{
   var type = $("#plot_type").val();
   if (type == "scatter_2d")
      {
         $(".wrapper_menu_2").css("height","140px");
         $(".scatter_2d_plot").addClass("plot_menu_shown")
      }
  else
      {
         $(".wrapper_menu_2").css("height","90px");
         $(".scatter_2d_plot").removeClass("plot_menu_shown");
      }
  if (type == "histogram")
      {
         $(".wrapper_menu_2").css("height","140px");
         $(".histogram_plot").addClass("plot_menu_shown")
      }
  else
      {
         $(".wrapper_menu_2").css("height","90px");
         $(".histogram_plot").removeClass("plot_menu_shown");
      }
      
      
      
  if (type == "biv_hist")
      {
         $(".wrapper_menu_2").css("height","140px");
         $(".biv_histogram_plot").addClass("plot_menu_shown")
      }
  else
      {
         $(".wrapper_menu_2").css("height","90px");
         $(".biv_histogram_plot").removeClass("plot_menu_shown");
      }
      
      
      
      
      
  if (type == "line")
      {
         $(".wrapper_menu_2").css("height","140px");
         $(".line_plot").addClass("plot_menu_shown")
      }
  else
      {
         $(".wrapper_menu_2").css("height","90px");
         $(".line_plot").removeClass("plot_menu_shown");
      } 
};

 $(function(){     
    $("#selectall_button").click(function(){
      var type = $("#sunspot_type").val();
      if (type == "magnetogram") {
        $("[name='attributes']").prop("checked",true); 
        $("[class='magnetogram']").prop("checked",true);
        $("[class='continuum']").removeAttr("checked");
      }
      else if (type == "continuum") { 
        $("[name='attributes']").prop("checked",true); 
        $("[class='continuum']").prop("checked",true);
        $("[class='magnetogram']").removeAttr("checked");
      }
    })

    $("#clearall_button").click(function(){     
      $("[name='attributes']").removeAttr("checked"); 
    });
});

$(function () {
  $('#database_button').click(function () {
    if ($(this).hasClass('menu-open')) {
      $(this).removeClass('menu-open');
      $('#filter_menu_showmore').css('display','none');
      $('#show_button').css('display','block');
      $('#filter_menu').css('height','195');

      $('#side_menu').animate({
        left: '-330'
      })
    } else {
      $(this).addClass('menu-open');
      $('#side_menu').animate({
        left: '0'
      })
    }
  })
});

$(function () {
  $('#statistics_button').click(function () {
    if ($(this).hasClass('table-close')) {
      $(this).removeClass('table-close');
      $('#wrapper_table_block').css('top','auto');
      $('#wrapper_table_block').animate({
        bottom: '-90%'
      });
    } else {
      $(this).addClass('table-close');
      $('#wrapper_table_block').css('top','auto');
      $('#wrapper_table_block').animate({
        bottom: '0'
      });
    }
  })
});

$(function() {
    $( "#wrapper_image" ).draggable({ 
      cursor: "move",
      cancel: "#image",
      containment: "#wrapper_body"
    });
    $( "#wrapper_table_block" ).draggable({ 
      cursor: "move",
      cancel: "#wrapper_table_info",
      containment: "#wrapper_body"
    });
    $( "#bokeh_plot" ).draggable({ 
      cursor: "move",
      cancel: ".bk-plot-layout",
      containment: "#wrapper_body"
    });
    $( "#wrapper_table_block" ).resizable({
      handles:'all',
      autoHide:true
    });
    $( "#wrapper_image" ).resizable({
      handles:'all',
      autoHide:true
    });
      });

$(function () {
  $('#reset_button').click(function () {
      $('.ui-wrapper').css('height','70vh').css('width','67.8vw').css('left','0').css('top','0');
      $('#image').css('height','100%').css('width','100%');
      $('#wrapper_image').css('top','0').css('left','0');
      $('#wrapper_table_block').css('top','auto').css('buttom','0').css('left','15%');
  })
});

$(function () {
  $('#help_button').click(function () {
      window.location.href='/help.html';
  })
});

$(function () {
  $('#download_button').click(function () {
      if ($(this).hasClass('options-open')) {
      $(this).removeClass('options-open');
      $('.download_options').fadeOut(400);
    } else {
      $(this).addClass('options-open');
      $('.download_options').fadeIn(400);
    }
  })
});

$(function () {
  $('#wrapper_body').click(function () {
      if ($('#download_button').hasClass('options-open')) {
      $('#download_button').removeClass('options-open');
      $('.download_options').fadeOut(400);
    }
  })
});

$(function(){
  $('#wrapper_table_info').mouseover(function(){
    $('#wrapper_table').css('overflow-x','scroll');
    $('#wrapper_table').css('overflow-y','scroll');
  });
  $('#wrapper_table_info').mouseleave(function(){
    $('#wrapper_table').css('overflow-x','hidden');
    $('#wrapper_table').css('overflow-y','hidden');
  })
});

$(function(){
  $('#wrapper_image_minimum_button').click(function(){
    $('#wrapper_image').css('display','none');
    $('#a').css('display','table')
  });
  $('#a').click(function(){
    $('#wrapper_image').css('display','block');
    $('#a').css('display','none')
  });
  $('#wrapper_image_close_button').click(function(){
     $('#wrapper_image').css('display','none');
  });

  $('#wrapper_table_minimum_button').click(function(){
    $('#wrapper_table_block').css('display','none');
    $('#b').css('display','table')
  });
  $('#b').click(function(){
    $('#wrapper_table_block').css('display','block');
    $('#b').css('display','none')
  });
  $('#wrapper_table_close_button').click(function(){
     $('#wrapper_table_block').css('display','none');
  });

  $('#bokeh_plot_minimum_button').click(function(){
    $('#bokeh_plot').css('display','none');
    $('#c').css('display','table')
  })
  $('#c').click(function(){
    $('#bokeh_plot').css('display','block');
    $('#c').css('display','none')
  })
});

$(function(){
  $('#wrapper_image_windowBar').click(function(){
    $('#wrapper_image').addClass('windowBar_shown')
    if ($('#bokeh_plot').hasClass('windowBar_shown')) {
      $('#bokeh_plot').removeClass('windowBar_shown');
    }
    if ($('#wrapper_table_block').hasClass('windowBar_shown')) {
      $('#wrapper_table_block').removeClass('windowBar_shown');
    }

  });
  $('#wrapper_table_windowBar').click(function(){
    $('#wrapper_table_block').addClass('windowBar_shown')
    if ($('#bokeh_plot').hasClass('windowBar_shown')) {
      $('#bokeh_plot').removeClass('windowBar_shown');
    }
    if ($('#wrapper_image').hasClass('windowBar_shown')) {
      $('#wrapper_image').removeClass('windowBar_shown');
    }

  });
  $('#bokeh_plot_windowBar').click(function(){
    $('#bokeh_plot').addClass('windowBar_shown')
    if ($('#wrapper_table_block').hasClass('windowBar_shown')) {
      $('#wrapper_table_block').removeClass('windowBar_shown');
    }
    if ($('#wrapper_image').hasClass('windowBar_shown')) {
      $('#wrapper_image').removeClass('windowBar_shown');
    }

  })
});
