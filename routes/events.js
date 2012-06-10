var Sequelize = require('sequelize');

var db = new Sequelize('ssi','dev','dev', {
	host: "localhost"
});

exports.index = 