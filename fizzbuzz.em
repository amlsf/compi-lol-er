fun (int maxNum, string pointless, int wtf) -> fizzBuzz -> int { 
	
	call num itemin bounds(0:maxNum!-1) {
		if (num % 3 == 0) { 
			log("Fizz");
		}
		if (num % 5 == 0) {
			log("Buzz");
		}
		elif (num % 3 != 0) {
			log(num);
		}
	}
}

var string|blah = "interrupting variables on top of stack and ish";
send(5, "DERP", 100) -> fizzbuzz;