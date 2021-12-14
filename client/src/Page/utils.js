export const range = (min, max) =>
	Array.from(new Array(max - min + 1).keys()).map(function (num) {
		return num + min;
	});
