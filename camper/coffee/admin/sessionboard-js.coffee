
Array::toDict = (key) ->
    @reduce ((dict, obj) -> dict[ obj[key] ] = obj if obj[key]?; return dict), {}

s4 = () ->
    Math.floor((1 + Math.random()) * 0x10000)
           .toString(16)
           .substring(1)

guid = () ->
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
           s4() + '-' + s4() + s4() + s4()

Handlebars.registerHelper "formatTime", (datetime, format) ->
    format = "HH:mm"
    return moment(datetime).tz('UTC').format(format)
  

$.fn.serializeObject = () ->
    o = {}
    a = this.serializeArray()
    $.each a, () ->
        if o[this.name] != undefined
            if not o[this.name].push
                o[this.name] = [o[this.name]]
            o[this.name].push(this.value || '')
        else
            o[this.name] = this.value || ''

    return o

do ( $ = jQuery, window, document ) ->


    pluginName = "sessionboard"
    defaults =
        foo: "bar"

    class Plugin
        constructor: (@element, options) ->

            @version = 0
            @data = {}
            @options = $.extend {}, defaults, options

            @_defaults = defaults
            @_name = pluginName

            @init()

        init: () ->


            $(@element).on 'update', () =>
                @saveState()
                @render()
            @loadState()

        loadState: () ->
            $.ajax
                url: "sessionboard/data"
                dataType: 'json'
                cache: false
                success: (data) =>
                    @data = data
                    @render()
                error: (xhr, status, err) =>
                    console.error("url", status, err.toString())

        saveState: () ->

            data =
                rooms: this.data.rooms
                timeslots: this.data.timeslots
                sessions: this.data.sessions
            $.ajax
                url: "sessionboard/data"
                data : JSON.stringify(this.data)
                contentType : 'application/json'
                type : 'POST'
                success: (data) =>
                    console.log "ok"
                error: (data) =>
                    console.log "not so ok"

        render: () ->
            console.log @data
            colwidth = 90/(this.data.rooms.length+1)
            html = JST["sessiontest"](
                data: @data
                colwidth: colwidth
                version: @version
            )
            $("#newsessions").html(html)
            this.init_handlers()
            this.version = this.version + 1

        add_room_modal: () =>
            html = JST["room-modal"](
                add_room: true
            )
            $("#modals").html(html)
            $('#add-room-modal').modal('show')
            $('#room-form-name').focus()

            $(".add-room-button").click @add_room
            return false

        add_room: () =>
            room = $("#add-room-form").serializeObject()
            room.id = guid()
            if !room.name
                return alert("Please enter a name")
            if !room.capacity
                return alert("Please enter a capacity")
            @data.rooms.push(room)
            $("#newsessions").trigger("update")
            $('#add-room-modal').modal('hide')
            return

        del_room: (event) =>
            ###
            delete a room after asking for confirmation
            ###
            if confirm($('body').data("i18n-areyousure"))
                idx = $(event.currentTarget).data("index")
                @data.rooms.splice(idx,1)
                $("#newsessions").trigger("update")

        edit_room_modal: (event) =>
            idx = $(event.currentTarget).data("index")
            room = @data.rooms[idx]
            html = JST["room-modal"](
                room: room
                room_idx: idx
                add_room: false
            )
            $("#modals").html(html)
            $('#add-room-modal').modal('show')
            $('#room-form-name').focus()
            $(".update-room-button").click @edit_room
            false

        edit_room: (event) =>
            room = $("#add-room-form").serializeObject()
            room_idx = room['room_idx']
            if !room_idx
                return alert("Error")
            if !room.name
                return alert("Please enter a name")
            if !room.capacity
                return alert("Please enter a capacity")
            room = JSON.parse(JSON.stringify(room))
            @data.rooms[room_idx] = room
            $("#newsessions").trigger("update")
            $('#add-room-modal').modal('hide')
            false

        set_next_time: () ->
            ###
            computes the next possible time for the timeslot modal
            ###

            l = @data.timeslots.length
            if l
                last_time = new Date(@data.timeslots[l-1].time)
                last_time = new Date(last_time.getTime() + last_time.getTimezoneOffset() * 60000) # convert to UTC
                new_time = new Date(last_time.getTime() + 60*60000)
                $("#timepicker").timepicker('setTime', new_time)
            else
                d = Date.now() # TODO: set the date of the day of the event
                dd = new Date()
                dd.setTime(d)
                dd.setHours(9)
                dd.setMinutes(0)
                dd.setSeconds(0)
                $("#timepicker").timepicker('option', 'minTime', '00:00')
                $("#timepicker").timepicker('setTime', dd)


        add_timeslot_modal: (event) =>
            ###
            show the timeslot modal and set the next available time
            ###

            # compute the new time and set the timepicker
            html = JST["timeslot-modal"]()
            $("#modals").html(html)
            $("#timepicker").timepicker
                timeFormat: "G:i"
                show24: true
            @set_next_time()
            $('#add-timeslot-modal').modal('show')
            $('#timepicker').focus()
            $("#add-timeslot-button").click @add_timeslot
            return false

        add_timeslot: (event) =>
            ###
            add a new timeslot to the list of timeslots
            ###

            timeslot = $("#add-timeslot-form").serializeObject()

            # get the local timezone offset
            now = new Date()
            localOffset = now.getTimezoneOffset()
            
            # convert to utc by removing the local offset
            entered_time = $("#timepicker").timepicker("getTime")

            utc = new Date(entered_time - localOffset*60000)
            
            timeslot.time = utc
            @data.timeslots.push timeslot
            
            $("#newsessions").trigger("update")
            $('#add-timeslot-modal').modal('hide')

            return





        # initialize all drag/drop/sortable handlers
        init_handlers: () ->

            that = this
            
            # sortable
            
            try
                room_dict = @data.rooms.toDict("id")
            catch
                room_dict = {}
            $("#roomcontainment").sortable
                axis: 'x'
                helper: "clone"
                items: "td"
                placeholder: "sortable-placeholder"
                containment: 'parent'
                cancel: ".not-sortable"
                opacity: 0.5
                update: (event, ui) =>
                    new_rooms = []
                    $("#newsessions #roomcontainment .sorted").each () ->
                        id = $(this).data("id")
                        new_rooms.push(room_dict[id])
                    @data.rooms = new_rooms
                    $("#newsessions").trigger("update")

            $("#add-room-modal-button").click @add_room_modal
            $(".del-room-button").click @del_room
            $(".edit-room-modal-button").click @edit_room_modal
            $("#add-timeslot-modal-button").click @add_timeslot_modal



    $.fn[pluginName] = ( options ) ->
        return this.each( () ->
            if  not $.data(this, "plugin_" + pluginName)
                $.data(this, "plugin_" + pluginName,
                    new Plugin( this, options ))
        )


$(document).ready () ->
    $("#newsessions").sessionboard()