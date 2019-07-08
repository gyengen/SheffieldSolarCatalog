
function openInNewTab(url) {
  var win = window.open(url, '_blank');
  win.focus();
}

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

function showmore(){
  document.getElementById("filter_menu_showmore").style.display="block";
  document.getElementById("show_button").style.display="none";
  document.getElementById("filter_menu").style.height=435;
  // document.getElementById("side_menu").style.top="10%";
  // document.getElementById("plotting_menu").style.top="10%";
}

function hide(){
  document.getElementById("filter_menu_showmore").style.display="none";
  document.getElementById("show_button").style.display="block";
  document.getElementById("filter_menu").style.height=195;
  // document.getElementById("side_menu").style.top="20%";
  // document.getElementById("plotting_menu").style.top="20%";
}

function change_sunspot_type(){     
  var type = $("#sunspot_type").val();
  if (type == "magnetogram") {
    $("#c_order_by").addClass("hide")
    $("#m_order_by").removeClass("hide")
    $("[name='attributes']").prop("checked",true); 
    $("[class='magnetogram']").removeAttr("disabled");
    $("[class='magnetogram']").prop("checked",true);
    $("[class='continuum']").prop("disabled",'disabled');
    $("[class='continuum']").removeAttr("checked");
    $("#type1_header").css("display","block");
    $("#type2_header").css("display","none");
  }
  else if (type == "continuum") {
    $("#m_order_by").addClass("hide")
    $("#c_order_by").removeClass("hide")
    $("[name='attributes']").prop("checked",true); 
    $("[class='continuum']").removeAttr("disabled");
    $("[class='continuum']").prop("checked",true);
    $("[class='magnetogram']").prop("disabled",'disabled');
    $("[class='magnetogram']").removeAttr("checked");
    $("#type2_header").css("display","block");
    $("#type1_header").css("display","none");
  }
};

function change_plot_type()
{
   var type = $("#plot_type").val();
   if (type != "none" && type != "kde") {
     if (type == "scatter_2d")
        {
           $("#plotting_menu").css("height","245px");
           $(".scatter_2d_plot").addClass("plot_menu_shown")
        }
      else
        {
           $(".scatter_2d_plot").removeClass("plot_menu_shown");
        }
      if (type == "histogram")
        {
           $("#plotting_menu").css("height","270px");
           $(".histogram_plot").addClass("plot_menu_shown")
        }
      else
        {
           $(".histogram_plot").removeClass("plot_menu_shown");
        }
        
      if (type == "biv_hist")
        {
           $("#plotting_menu").css("height","225px");
           $(".biv_histogram_plot").addClass("plot_menu_shown")
        }
      else
        {
           $(".biv_histogram_plot").removeClass("plot_menu_shown");
        }

      if (type == "line")
        {
           $("#plotting_menu").css("height","225px");
           $(".line_plot").addClass("plot_menu_shown")
        }
      else
        {
           $(".line_plot").removeClass("plot_menu_shown");
        } 
    }else{
      $("#plotting_menu").css("height","130px");
      $(".line_plot").removeClass("plot_menu_shown");
      $(".biv_histogram_plot").removeClass("plot_menu_shown");
      $(".histogram_plot").removeClass("plot_menu_shown");
      $(".scatter_2d_plot").removeClass("plot_menu_shown");
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
      $('#side_menu').fadeOut(0);
      $(this).css('z-index','0');
    } else {
      $(this).addClass('menu-open');
      $('#side_menu').fadeIn(100);
      $('#plotting_menu').fadeOut(0);
      $('#plot_button').removeClass('plot-open');
      $('.download_options').fadeOut(0);
      $('#download_button').removeClass('open');
      $('#side_menu').css('z-index','100');
      $('#plotting_menu').css('z-index','0');
      $('.download_options').css('z-index','0');


            $("#message_log").css("top","-230px");
            $("#message_log_bar").addClass('table-close');

    }
  })
});

$(function () {
  $('#plot_button').click(function () {
    if ($(this).hasClass('plot-open')) {
      $(this).removeClass('plot-open');
      $('#plotting_menu').fadeOut(0);
      $(this).css('z-index','0');
    } else {
      $(this).addClass('plot-open');
      $('#plotting_menu').fadeIn(100);
      $('#database_button').removeClass('menu-open');
      $('#side_menu').fadeOut(0);
      $('.download_options').fadeOut(0);
      $('#download_button').removeClass('open');
      $('#plotting_menu').css('z-index','100');
      $('#side_menu').css('z-index','0');
      $('.download_options').css('z-index','0');



            $("#message_log").css("top","-230px");
            $("#message_log_bar").addClass('table-close');

    }
  })
});

$(function () {
  $('#download_button').click(function () {
      if ($(this).hasClass('open')) {
      $(this).removeClass('open');
      $('.download_options').fadeOut(0);
      $(this).css('z-index','0');
    } else {
      $(this).addClass('open');
      $('.download_options').fadeIn(100);
      $('#side_menu').fadeOut(0);
      $('#database_button').removeClass('menu-open');
      $('#plotting_menu').fadeOut(0);
      $('#plot_button').removeClass('plot-open');
      $('.download_options').css('z-index','100');
      $('#side_menu').css('z-index','0');
      $('#plotting_menu').css('z-index','0');
    }
  })
});

$(function () {
  $('#statistics_button').click(function () {
      if ($('#wrapper_table_block').hasClass('table-minimized')==false) {
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
  }
  })
});

$(function() {
    $( "#wrapper_image" ).draggable({ 
      cursor: "move",
      handle:'#wrapper_image_windowBar'
    });
    $( "#wrapper_image2" ).draggable({ 
      cursor: "move",
      cancel: "#image",
      handle:'#wrapper_image_windowBar'
    });
    $( "#wrapper_table_block" ).draggable({ 
      cursor: "move",
      cancel: "#wrapper_table_info",
      containment: "#wrapper_body"
    });
    $( ".bokeh_plot" ).draggable({ 
      cursor: "move",
      cancel: ".bk-plot-layout",
      containment: "#wrapper_body"
    });
    $( "#wrapper_table_block" ).resizable({
      handles:'all',
      autoHide:true
    });
});



$(function () {
  $('#reset_button').click(function () {
      $('.ui-wrapper').css('height','70vh').css('width','67.8vw').css('left','0').css('top','0');
      $('#image').css('height','100%').css('width','100%');
      $('#wrapper_image').css('top','0').css('left','0').css('display',"block");
      $('#wrapper_image2').css('top','0').css('left','0').css('display',"block");
      $('.window1').css('display','none');
  })
});

$(function () {
  $('#help_button').click(function () {
      window.location.href='/help.html';
  })
});



$(function () {
  $('#wrapper_body').click(function () {
      if ($('#download_button').hasClass('options-open')) {
      $('#download_button').removeClass('options-open');
      $('.download_options').fadeOut(200);
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
});

$(function(){
  $('#wrapper_image_minimum_button2').click(function(){
    $('#wrapper_image2').css('display','none');
    $('#c').css('display','table')
  });
  $('#c').click(function(){
    $('#wrapper_image2').css('display','block');
    $('#c').css('display','none')
  });
  $('#wrapper_image_close_button2').click(function(){
     $('#wrapper_image2').css('display','none');
  });
});


$(function(){
  $('#wrapper_table_minimum_button').click(function(){
    $('#wrapper_table_block').css('display','none');
    $('#b').css('display','table');
    $('#wrapper_table_block').addClass('table-minimized')
  });
  $('#b').click(function(){
    $('#wrapper_table_block').css('display','block');
    $('#b').css('display','none')
    $('#wrapper_table_block').removeClass('table-minimized')
  });
  $('#wrapper_table_close_button').click(function(){
     $('#wrapper_table_block').css('display','none');
  });
});

$(function () {
  $('#message_log_bar').click(function () {
    if ($(this).hasClass('table-close')) {
      $(this).removeClass('table-close');
      $("#message_log").css("top","50px");

      $('#database_button').removeClass('menu-open');
      $('#side_menu').fadeOut(0);

      $('#plotting_menu').fadeOut(0);
      $('#plot_button').removeClass('plot-open');

    } else {
      $(this).addClass('table-close');
      $("#message_log").css("top","-230px");
    }
  })
});

$(function(){
  $('#filter-clear').click(function(){
    $("[class='value_input']").val('0');
  });
});

$(function(){
  $('.z-position').mousedown(function(){
    $(this).css('z-index', 9999);
    var list = $('.z-position').sort(function (a,b) {
      if (a.style.zIndex == '') {
          a.style.zIndex = 1
      }
      if (b.style.zIndex == '') {
          b.style.zIndex = 1
      }
      return (parseInt(a.style.zIndex,10) < parseInt(b.style.zIndex,10)) ? -1 : (parseInt(a.style.zIndex,10) > parseInt(b.style.zIndex,10)) ? 1 : 0;
    });
    var i = 1
    $.each(list, function(index,value) {
      $(this).css('z-index', i);
      i = i + 1;
    });
  });
});

$(function(){
  $('.AR_download_type').change(function(){
    if ($(this).val() == "pdf") {
      $(".pdf").css('display','block')
      $(".png").css('display','none')
    } else {
      $(".png").css('display','block')
      $(".pdf").css('display','none')
    }
  });
});


$(function(){
  $('.download_date_options').change(function(){
    $('.date_specific_image').each(function() {
      $(this).css('display','none')
    })
    var x = ("." + $(this).val()).replace(/\s/g, '').replace(/:/g,"")
    $(x).each(function() {
      $(this).css('display','block')
    })
  });
});

