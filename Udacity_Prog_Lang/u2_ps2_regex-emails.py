import re 

def addresses(haystack): 
  haystack = re.sub(r"NOSPAM", "", haystack) 
  print re.findall(r"(\w+@[a-zA-Z]+(?:\.[a-zA-Z]+)+)", haystack)
  return re.findall(r"\w+@[a-zA-Z]+(\.[a-zA-Z]+)+", haystack)

addresses("""louiseNOSPAMaston@germany.de (1814-1871) was an advocate for
democracy. irmgardNOSPAMkeun@NOSPAMweimar.NOSPAMde (1905-1982) wrote about
the early nazi era. rahelNOSPAMvarnhagen@berlin.de was honored with a 1994
deutsche bundespost stamp. seti@home is not actually an email address someemail@email.email.email.com.""")