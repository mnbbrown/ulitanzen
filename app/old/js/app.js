var LoggedIn = null;

var Guest = Backbone.Model.extend({
	defaults: {
		"id" : null,
		"name" : "",
		"email" : "",
		"seats_booked": 0,
		"paid" : false
	},
	url: function () {
		return "../api/guests/" + this.get("id");
	}
});

var GuestList = Backbone.Collection.extend({
	model: Guest,
	url: "../api/guests"
})

var GuestView = Backbone.View.extend({
	tagName: 'tr',
	className: 'guest-row',
	template: _.template($('#guest-row-template').html()),

	render: function(){
		this.$el.html(this.template(this.model.toJSON()))
		return this.$el
	}
})

var GuestsView = Backbone.View.extend({

	initialize: function(){
		this.collection = new GuestList();
		var self = this
		this.collection.fetch({success:function(collection){
			self.render()
		}})
	},

	render: function(){
		var self = this
		_(this.collection.models).each(function(guest){
			var guest_view = new GuestView({model:guest})
			self.$el.append(guest_view.render())
		})
	}
})

var GuestSelectorView = Backbone.View.extend({
	tagName: "select",
	id: "guest-select",

	initialize: function(){

	},

	render: function(){
		var self = this;
		console.log(this.collection)
		_(this.collection.models).each(function(guest){
			guest = guest.toJSON()
			self.$el.append('<option value="'+ guest.id +'">'+ guest.name +'</option>')
		})
		console.log(this)
		return this.$el
	}

});

var LoginView = Backbone.View.extend({

	el: $('#login'),

	events: {

	}

	initialize: function(){
		console.log(this.collection)
		this.render()
	},

	render: function(){
		var guest_selector = new GuestSelectorView({collection: this.collection})
		this.$el.append(guest_selector.render())
	}

});

var AppView = Backbone.View.extend({

	initialize: function(){
		var guests = new GuestList()
		guests.fetch({success:function(guests){
			login_view = new LoginView({collection: guests});
		}})
	}

});
var app = new AppView()
var guest_table = new GuestsView({el: $('table[id="guests"] tbody')})