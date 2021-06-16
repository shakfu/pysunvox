#export LD_LIBRARY_PATH=./lib:$LD_LIBRARY_PATH

all:
	@python3 setup.py build_ext -i
	@cp ./lib/libsunvox.dylib ./sunvox.dylib
	@xattr -r -d com.apple.quarantine ./sunvox.dylib

main:
	@gcc -I./include -L./lib -lsunvox -o main src/main.c
	@mkdir -p ./out
	@mv ./main ./out
	@cp ./lib/libsunvox.dylib ./out/sunvox.dylib
	@xattr -r -d com.apple.quarantine ./out

.PHONY: test reset clean

test:
	python3 -c "import sunvox;sunvox.play('resources/test0.sunvox')"
# 	python3 -c "import sunvox;sunvox.generate('resources/test.sunvox', 'out.wav')"

clean:
	@rm -rf build
	@rm -f sunvox.*.so
	@rm -f sunvox.dylib

reset: clean
	@rm -f src/sunvox.c
	@rm -rf ./out



