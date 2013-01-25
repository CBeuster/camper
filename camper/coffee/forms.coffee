class Editable

    constructor: (@elem, @options) ->
        @state = "view"
        @url = $(@elem).closest("form").attr("action")
        return this

    clicked: () ->
        @state = if @state == 'view' then 'edit' else 'view'
        if @state == "edit"
            @show_edit_field()

    show_edit_field: () ->
        field = $(@elem).data('field')
        $.ajax(
            url: @url
            type: 'GET'
            data: 
                field: field
            success: (data) =>
                @payload = $(@elem).html()
                $(@elem).html(data.html)
                @escape()
        )

    close_edit_field: () ->
        @state = "view"
        $(@elem).html(@payload)
        @escape()
    
    escape: () ->
        if @state == "view"
            $(document).off('keyup.editable.keys')
        else
            $(document).on('keyup.editable.keys', ( e ) =>
                e.which == 27 && @close_edit_field()
                e.which == 13 && console.log "enter"
                console.log "nö"
                e.preventDefault()
            )
            $(@elem).closest("form").submit( (e) ->
                console.log "okiiuij"
                e.preventDefault()
                return false
            )
            

$.fn.editable = (opts = {}) ->
    init = (opts) ->
        $this = $(this)
        data = $(this).data('editable')
        options = typeof opts == 'object' && opts
        if not data 
            data = new Editable(this, options)
            $this.data('editable', data)
        data.clicked()

    $(this).each(init)
    this

# run this on input fields to limit the input to only chars and numbers without spaces
$.fn.limitchars = (opts = {}) ->
    init = (opts) ->
        $this = $(this)
        allowed ='1234567890abcdefghijklmnopqrstuvwxyz-_'
        $(this).keypress( (e) ->
            k = parseInt(e.which)
            if k!=13 and k!=8 and k!=0
                if (e.ctrlKey == false) and (e.altKey == false) 
                    return allowed.indexOf(String.fromCharCode(k)) != -1
                else
                    return true
            else
                return true
        )
    $(this).each(init)
    this

$(document).ready( () ->
    $(".urlscheme").limitchars()
    $(".form-validate").validate(
        showErrors: (errorMap, errorList) ->
            $.each( this.successList , (index, value) ->
                $(value).removeClass("error")
                $(value).popover('hide')
            )
            form = this.currentForm
            position = $(form).data("errorposition") or 'right'
            $.each( errorList , (index, value) ->
                _popover = $(value.element).popover(
                        trigger: 'manual'
                        placement: position
                        content: value.message
                        template: '<div class="popover error"><div class="arrow"></div><div class="popover-inner"><div class="popover-content"><p></p></div></div></div>'
                )

                _popover.data('popover').options.content = value.message
                $(value.element).addClass("error")
                $(value.element).popover('show')
            );
    )
    $("#sponsor-form").validate(
        rules: {
          "upload-value-id": {
            required: true
          },
        },

        submitHandler: (form) ->
            if $(form).find(".upload-value-id").val()
                form.submit()
            else
                alert("Bitte lade ein Logo hoch")
    
        highlight: (label) ->
            $(label).closest('.control-group').addClass('error')
        success: (label) ->
            label
                .text('OK!').addClass('valid')
                .closest('.control-group').addClass('success')
    )

    $('body').on("click.editable", '[data-toggle="editable"]', (e) ->
        $(e.target).editable()
    )
)
