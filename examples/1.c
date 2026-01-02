#include <stdio.h>

void main(){
	long int s=0;
	int n=99999;
	for (int i=0; i<n; i++){
		s+=i;
	}
	printf("%ld", s);

}
