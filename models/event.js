exports.event = function(db, DataType){
	
	return db.define('Event', {
		title: {
			type: DataTypes.STRING, 
			allowNull: false,
			validate: {
				notNull: true,
				notEmpty: true
			}
		},
		description: {
			type: DataTypes.STRING, 
			allowNull: true
		},
		start_date: {
			type: DataTypes.DATE, 
			allowNull: false,
			validate: {
				notNull: true,
				notEmpty: true,
				isDate: true
			}
		},
		end_date: {
			type: DataTypes.DATE, 
			allowNull: false,
			validate: {
				notNull: true,
				notEmpty: true,
				isDate: true
			}
		},
		tz: {
			type: DataTypes.INTEGER, 
			allowNull: false,
			validate: {
				notNull: true,
				notEmpty: true,
				isDate: true,
				len: [2,3]
			}
		},
		capacity: {type: DataTypes.INTEGER, allowNull: true}, 
		status: {type: DataTypes.STRING, allowNull: true}
		}, {
		timestamps: false
	});
	
}

 