$.fn.dataTableExt.oApi.fnPagingInfo=function(e){return{iStart:e._iDisplayStart,iEnd:e.fnDisplayEnd(),iLength:e._iDisplayLength,iTotal:e.fnRecordsTotal(),iFilteredTotal:e.fnRecordsDisplay(),iPage:e._iDisplayLength===-1?0:Math.ceil(e._iDisplayStart/e._iDisplayLength),iTotalPages:e._iDisplayLength===-1?0:Math.ceil(e.fnRecordsDisplay()/e._iDisplayLength)}},$.extend($.fn.dataTableExt.oPagination,{bootstrap:{fnInit:function(e,t,n){var r=e.oLanguage.oPaginate,i=function(t){t.preventDefault(),e.oApi._fnPageChange(e,t.data.action)&&n(e)};$(t).append('<ul class="pagination"><li class="prev disabled"><a href="#"><i class="icon-double-angle-left"></i> '+r.sPrevious+"</a></li>"+'<li class="next disabled"><a href="#">'+r.sNext+' <i class="icon-double-angle-right"></i></a></li>'+"</ul>");var s=$("a",t);$(s[0]).bind("click.DT",{action:"previous"},i),$(s[1]).bind("click.DT",{action:"next"},i)},fnUpdate:function(e,t){var n=5,r=e.oInstance.fnPagingInfo(),i=e.aanFeatures.p,s,o,u,a,f,l=Math.floor(n/2);r.iTotalPages<n?(a=1,f=r.iTotalPages):r.iPage<=l?(a=1,f=n):r.iPage>=r.iTotalPages-l?(a=r.iTotalPages-n+1,f=r.iTotalPages):(a=r.iPage-l+1,f=a+n-1);for(s=0,iLen=i.length;s<iLen;s++){$("li:gt(0)",i[s]).filter(":not(:last)").remove();for(o=a;o<=f;o++)u=o==r.iPage+1?'class="active"':"",$("<li "+u+'><a href="#">'+o+"</a></li>").insertBefore($("li:last",i[s])[0]).bind("click",function(n){n.preventDefault(),e._iDisplayStart=(parseInt($("a",this).text(),10)-1)*r.iLength,t(e)});r.iPage===0?$("li:first",i[s]).addClass("disabled"):$("li:first",i[s]).removeClass("disabled"),r.iPage===r.iTotalPages-1||r.iTotalPages===0?$("li:last",i[s]).addClass("disabled"):$("li:last",i[s]).removeClass("disabled")}}}}),$(function(){$(".datatable").each(function(){var e=$(this),t=e.closest(".dataTables_wrapper").find("div[id$=_filter] input");t.attr("placeholder","Search"),t.addClass("form-control input-small"),t.css("width","250px");var n=e.closest(".dataTables_wrapper").find("div[id$=_filter] a");n.html('<i class="icon-remove-circle icon-large"></i>'),n.css("margin-left","5px");var r=e.closest(".dataTables_wrapper").find("div[id$=_length] select");r.addClass("form-control input-small"),r.css("width","75px");var r=e.closest(".dataTables_wrapper").find("div[id$=_info]");r.css("margin-top","18px")})});