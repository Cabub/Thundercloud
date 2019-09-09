const interface = {
  pwd: root_dir,
  init: function(){
    this.load_directory(this.pwd);
    $('#add-file-file').change(function(e) {
      if ($(e.target)[0].files.length && $('#add-file-name').val() == ''){
        $('#add-file-name').val($(e.target)[0].files[0].name);
      }
    });
    $("#add-file-form").submit(function(e) {
        e.preventDefault();
        let form = $(this);
        let url = form.attr('action');
        let method = form.attr('method');
        let data = new FormData(this);
        $.ajax({
           method: method,
           url: url,
           data: data,
           contentType: false,
           processData: false,
           success: function(data) {
             $('#add-file-name').val('');
             $('#add-file-file').val('');
             interface.load_directory(interface.pwd);
           },
           beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
         });
    });
    $("#add-folder-form").submit(function(e) {
      let form = $(this);
      let url = form.attr('action');
      let method = form.attr('method');
      $.ajax({
         method: method,
         url: url,
         data: form.serialize(),
         success: function(data) {
           $('#add-folder-name').val('');
           interface.load_directory(interface.pwd);
         },
         beforeSend: function(xhr, settings) {
              if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                  xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
              }
          }
       });

        e.preventDefault();
    });
  },
  load_directory: function(dir, path){
      let list = $('#directory_listing');
      list.html('');
      $.ajax({
        url: `/files/api/v1/folder/${dir}/list`,
        success: function(response){
          interface.pwd = this.pwd;
          $('#add-folder-parent').val(this.pwd);
          $('#add-file-parent').val(this.pwd);
          let list = $('#directory_listing');
          $('#pwd').text(response.path);
          if (typeof(response.parent) !== 'undefined'){
            let li = $('<li>');
            let link = $('<a>').data('id', response.parent);
            link.click(function(){
              let id = $(this).data('id');
              interface.load_directory(id);
            });
            link.text('(dir) ..');
            li.html(link);
            list.append(li);
          }
          for (item of response.children){
            let li = $('<li>');
            let link = $('<a>')
              .data('id', item.id)
              .data('type', item.type);
            link.click(function(){
              let id = $(this).data('id');
              let type = $(this).data('type');
              if (type == 'd')
                interface.load_directory(id);
              else
                window.location = `/files/api/v1/file/${id}/download`;
            });
            let text = '';
            if (item.type == 'd'){
              text += '(dir) ';
            }
            text += item.name;
            link.text(text);
            li.html(link);
            list.append(li);
          }
        },
        context: {
          pwd: dir
        }
      })
  }
}

$(function(){
  interface.init();
});
