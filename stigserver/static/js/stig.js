function CommentCtrl ($scope, $timeout, $http) {
	$scope.comment = {
		photo: 'https://fbcdn-sphotos-a-a.akamaihd.net/hphotos-ak-ash4/482258_10200159621925860_1616117691_n.jpg',
		stickers: 'H U E',
		name: 'Alexandre F',
		place: 'The Joker Pub',
		comment: 'Lorem ipsum dolor sit amet, consectetur adipisicing elit.',
	};

	var updateComment = function () {
		$http.get('home_comment').success(function (data) {
			// var comment = JSON.parse(data);
	        $scope.comment = data;
	    });
		$timeout(updateComment, 5000);
	}

	$timeout(updateComment, 5000);
}