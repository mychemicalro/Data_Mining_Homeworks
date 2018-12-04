import math

def main():
	array = [1,2,3,10,13,27,29,30]
	w = len(array) + 1
	h = 4 # h-1 is k 

	# 4x9 matrix of zeros
	matrix = [[0 for x in range(w)] for y in range(h)] 

	# iterating only after row 0, and column 0
	for i in range(1, h):
		for m in range(1, w):
			#matrix = D(matrix, array, i, m)
			if i == 1:
				matrix[i][m] = round(CC(array, i, m), 2)
			else:
				matrix[i][m] = round(D(matrix, array, i, m), 2)

	#print points
	print "points:"
	print array
	# print final matrix
	print "final matrix:"
	for row in matrix:
		for val in row:
			print '{:4}'.format(val),
		print

def CC(arr, i, m):
	result = 0
	mu = compute_mu(arr, i, m)
	squares = 0
	for i in arr[i-1:m]:
		squares = squares + abs(i-mu)**2
	return squares

def compute_mu(arr, i, j):
	denom = j-i+1
	nom = sum(arr[i-1:j])
	return nom / float (denom)

def D(matrix, arr, i, m):
	minimum = 12412312
	min_j = 0
	min_m = 0
	for j in range(1, m+1):
		if minimum > matrix[i-1][j-1] + CC(arr, j, m):
			minimum = matrix[i-1][j-1] + CC(arr, j, m)
			min_m = m
			min_j = j

		#minimum = min(minimum, matrix[i-1][j-1] + CC(arr, j, m))
	print "i=", i, "m=",m, "min j, m", min_j, min_m
	return minimum

main()