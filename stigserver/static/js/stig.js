function CommentCtrl ($scope, $timeout, $http) {
	$scope.comment = {
		photo: '',
		stickers: '',
		name: '',
		place: '',
		comment: '',
	};

	var updateComment = function () {
		$http.get('home_comment').success(function (data) {
			// var comment = JSON.parse(data);
	        $scope.comment = data;
	    });
		$timeout(updateComment, 6500);
	}

	$timeout(updateComment, 1);
}