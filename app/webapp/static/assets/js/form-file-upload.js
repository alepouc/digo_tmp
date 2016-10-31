Dropzone.options.myAwesomeDropzone = {
          paramName: "file",
          maxFilesize: 10,
          url: '/upload',
          uploadMultiple: true,
          parallelUploads: 5,
          maxFiles: 20,
          init: function() {
              var cd;
              this.on("success", function(file, response) {
                  $('.dz-progress').hide();
                  $('.dz-size').hide();
                  $('.dz-error-mark').hide();
                  console.log(response);
                  console.log(file);
                  cd = response;
              });
              this.on("addedfile", function(file) {
                  var removeButton = Dropzone.createElement("<a href=\"#\">Remove file</a>");
                  var _this = this;
                  removeButton.addEventListener("click", function(e) {
                      e.preventDefault();
                      e.stopPropagation();
                      _this.removeFile(file);
                      var name = "largeFileName=" + cd.pi.largePicPath + "&smallFileName=" + cd.pi.smallPicPath;
                      $.ajax({
                          type: 'POST',
                          url: 'DeleteImage',
                          data: name,
                          dataType: 'json'
                      });
                  });
                  file.previewElement.appendChild(removeButton);
              });
          }
      };
