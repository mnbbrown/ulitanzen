jQuery.fn.animateHighlight = function(highlightColor, duration) {
    var highlightBg = highlightColor || "#ED1842";
    var animateMs = duration || 1500;
    var originalBg = this.css("color");
    this.stop().css("color", highlightBg).animate({color: originalBg}, animateMs);
};

function tableGenerator(positions, reservations, users) {

	var t = 1;
	while (t < 12) {
		tID = "t" + t;
		tElement = "<div id=\"" + tID + "\"></div>";
		jQuery("#container").append(tElement);
		jQuery("#" + tID).addClass("table");
		jQuery("#" + tID).css({
			left: positions[1][t]["x"],
			top: positions[1][t]["y"]
		});
		jQuery("#" + tID).each(function() {
			p = 0;
			jQuery(this).append("<span class=\"tLabel\">Tisch " + tID.substr(1) + "</span>");
			while (p < 10) {
				sID = tID + "-p" + p;
				seat = jQuery("<a href=\"#\" id=\"" + sID + "\"></a>");
				jQuery(this).append(seat);
				seat.addClass("seat");
				if (reservations[t][p+1] !== null) {
				    reB = getUserName(reservations[t][p+1], users);
					seat.attr("title","Reserviert von: " + reB);
					addToolTip(seat, p+1)
					seat.removeAttr("href");
					seat.addClass("reserved");
				} else if(reservations[t][p+1] === null) {
					seat.attr("title", "Noch nicht reserviert");
					addToolTip(seat, p+1)
					seat.addClass("free");
					seat.click(seatReserve(t, p + 1));
				}

				seat.css({
					left: positions[0][p]["x"],
					top: positions[0][p]["y"]
				});
				p++;
			}
		});
		t++;
	}
}

function addToolTip(seat, seatCount){

	if(seatCount > 3 && seatCount < 9){
		seat.tipsy({gravity: 's'});
	}else{
		seat.tipsy();
	}

}

function getUserName(id, names){
	for(f in names){
		if(names[f]["id"] === id) {
			return f;
		}

	}

}

function elePositions() {

	var positions = new Array(Array(), Array());

	var sp = 0;
	var t = 0;

	while (sp < 10) {
		positions[0][sp] = new Array();
		positions[0][sp]["x"] = null;
		positions[0][sp]["y"] = null;
		sp++;
	}

	while (t < 12) {
		positions[1][t] = new Array();
		positions[1][t]["x"] = null;
		positions[1][t]["x=y"] = null;
		t++;
	}

	positions[0][0]["x"] = "41%";
	positions[0][0]["y"] = "6%";
	positions[0][1]["x"] = "62%";
	positions[0][1]["y"] = "13%";
	positions[0][2]["x"] = "75%";
	positions[0][2]["y"] = "30%";
	positions[0][3]["x"] = "75%";
	positions[0][3]["y"] = "52%";
	positions[0][4]["x"] = "62%";
	positions[0][4]["y"] = "70%";
	positions[0][5]["x"] = "41%";
	positions[0][5]["y"] = "76%";
	positions[0][6]["x"] = "21%";
	positions[0][6]["y"] = "70%";
	positions[0][7]["x"] = "8%";
	positions[0][7]["y"] = "51%";
	positions[0][8]["x"] = "8%";
	positions[0][8]["y"] = "30%";
	positions[0][9]["x"] = "21%";
	positions[0][9]["y"] = "13%";


	positions[1][1]["x"] = "0";
	positions[1][1]["y"] = "0";
	positions[1][2]["x"] = "0";
	positions[1][2]["y"] = "200px";
	positions[1][3]["x"] = "0";
	positions[1][3]["y"] = "400px";
	positions[1][4]["x"] = "0";
	positions[1][4]["y"] = "600px";
	positions[1][5]["x"] = "200px";
	positions[1][5]["y"] = "550px";
	positions[1][6]["x"] = "400px";
	positions[1][6]["y"] = "500px";
	positions[1][7]["x"] = "600px";
	positions[1][7]["y"] = "550px";
	positions[1][8]["x"] = "800px";
	positions[1][8]["y"] = "600px";
	positions[1][9]["x"] = "800px";
	positions[1][9]["y"] = "400px";
	positions[1][10]["x"] = "800px";
	positions[1][10]["y"] = "200px";
	positions[1][11]["x"] = "800px";
	positions[1][11]["y"] = "0";


	return positions;

}

$(document).ready(function() {

	initDisplay();

});

function initDisplay() {
	jQuery("#modalWelcome").text("Bitte Warten... Es wird geladen");
	jQuery("#nameInput").hide();
	jQuery("#nameGo").hide();
	var reservations = new Array();
	for(var i= 1; i<12;i++) {
		reservations[i] = new Array()
	}
	names = new Array();
	users = new Array();

	jQuery.getJSON("http://localhost:5000/api/guests", success = function(data) {
		jQuery.each(data, function(index, value) {
			users[value.name] = new Array();
			users[value.name]["id"] = value.id;
			users[value.name]["places"] = value.seats_booked;
			users.length++;
			names.push(value.name);
			jQuery("#nameInput").append("<option value=\"" + value.name + "\">" + value.name + "</option>");
		});
		console.log(users);
		jQuery("#welcome").bind('submit',function() {
			userInit(names, users);
			return false;
		});
		jQuery.getJSON("http://localhost:5000/api/seats", success = function(data) {
			jQuery.each(data, function(index, value) {
				if(value.table_number !== 0 || value.number !== 0) {
					reservations[value.table_number][value.number] = value.guest_id;
				}
			});
			console.log(reservations)
			tableGenerator(elePositions(), reservations, users);
			jQuery("#nameInput").show();
			jQuery("#nameGo").show();
			jQuery("#modalWelcome").text("Willkommen, Bitte Namen auswählen:");
			jQuery("#modalWelcome").animateHighlight();

		});
	});




}

function userInit(names,users) {
	currentUser = jQuery("#nameInput").val();

	if(jQuery.inArray(currentUser, names) < 0){
		console.log("Problem");
		jQuery("#welcomeBox").animate({height: "200px"}, 1000)
		jQuery("#errorMessage").show();
		jQuery("#errorMessage").animateHighlight();

	}else if(jQuery.inArray(currentUser, names) >= 0){
		console.log("OK... Init Welcome Screen");
		jQuery("#welcomeBox").hide();
		jQuery("#mask").hide();

		if (users[currentUser]["places"] <= 0) {
			finish();
		}

		jQuery("#userName").text(currentUser);
		jQuery("#userSeats").val(users[currentUser]["places"]);
		jQuery("#userSeatCount").text(users[currentUser]["places"]);
		jQuery("#userID").val(users[currentUser]["id"]);
		jQuery("#info").show();

	}

}

function finish() {

	jQuery("#mask").show();
	jQuery("#goodbyeBox").show();


}



function seatReserve(table, seatID) {

	return function() {
		console.log("reserve: " + table + " " + seatID)
		sID = "#t" + table + "-p" + (seatID - 1);
		seat = jQuery(sID);

		seat.removeAttr("href");
		seat.removeClass("free");
		seat.addClass("reserved");
		seat.unbind("click");
		seat.attr("title","Reserviert von: " + jQuery("#userName").text());
		addToolTip(seat, seatID);

		jQuery.getJSON("http://localhost:5000/api/seats", success = function(data) {
			var reservations = new Array();
			for(var i= 1; i<12;i++) {
				reservations[i] = new Array()
			}
			jQuery.each(data, function(index, value) {
				if(value.table_number !== 0 || value.number !== 0) {
					reservations[value.table_number][value.number] = value.guest_id;
				}
			});


			if(reservations[table][seatID] === null){
				var id = (10*parseInt(table)-10)+parseInt(seatID)
				var url = "http://localhost:5000/api/seats/" + id.toString()
				console.log(url)
				jQuery.ajax({
					url: url,
					type: "PUT",
					data: {"guest_id" : jQuery("#userID").val()},
					dataType: "json",
					beforeSend: function(x) {
					    if (x && x.overrideMimeType) {
					       x.overrideMimeType("application/json;charset=UTF-8");
					    }
					}
				});
			}else if(reservations[table][seatID] !== null){

				seat.attr("title","Soeben reserviert. Sorry!");
				addToolTip(seat, seatID);
				jQuery("#infoMessage").show();
				jQuery("#infoMessage").animateHighlight();

			}


		});


		count = jQuery("#userSeatCount").text();
		count--;
		if (count === 1) {
			jQuery("#seatCountLabel").text("Sitz");
		}

		if (count === 0) {
			jQuery(".seat").unbind("click");
			jQuery(".seat").removeAttr("href");
			finish();
		}

		jQuery("#userSeatCount").text(count);

	}
}