all:
	cp ../../resources/* ./
	gcc $(CFLAGS) -g -c test1.c
	gcc $(CFLAGS) -g -c test2.c
	gcc $(CFLAGS) -g -c test3.c
	gcc $(CFLAGS) -g -c test4.c
	gcc $(CFLAGS) -g -c test5.c
	gcc $(CFLAGS) -g -c test6.c
	gcc $(CFLAGS) -g -c test7.c
	gcc $(LDFLAGS) -o test1 test1.o
	gcc $(LDFLAGS) -o test2 test2.o
	gcc $(LDFLAGS) -o test3 test3.o
	gcc $(LDFLAGS) -o test4 test4.o
	gcc $(LDFLAGS) -o test5 test5.o
	gcc $(LDFLAGS) -o test6 test6.o
	gcc $(LDFLAGS) -o test7 test7.o

clean:
	rm -f *.o *.so *.dylib test1 test2 test3 test4 test5 test6 test7 *.sunvox *.sunsynth *.xi *.wav
