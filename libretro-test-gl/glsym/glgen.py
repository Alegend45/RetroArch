#!/usr/bin/env python3

import sys
import os
import re

banned_ext = [ 'AMD', 'APPLE', 'EXT', 'NV', 'NVX', 'ATI', '3DLABS', 'SUN', 'SGI', 'SGIX', 'SGIS', 'INTEL', '3DFX', 'IBM', 'MESA', 'GREMEDY', 'OML', 'PGI', 'I3D', 'INGL', 'MTX', 'QCOM', 'IMG', 'ANGLE', 'SUNX', 'INGR' ]

def noext(sym):
   for ext in banned_ext:
      if sym.endswith(ext):
         return False
   return True

def find_gl_symbols(lines):
   typedefs = []
   syms = []
   for line in lines:
      m = re.search(r'^typedef.+PFN(\S+)PROC.+$', line)
      g = re.search(r'^.+(gl\S+)\W*\(.+\).*$', line)
      if m and noext(m.group(1)):
         typedefs.append(m.group(0).replace('PFN', 'RGLSYM'))
      if g and noext(g.group(1)):
         syms.append(g.group(1))
   return (typedefs, syms)

def generate_defines(gl_syms):
   res = []
   for line in gl_syms:
      res.append('#define {} __rglgen_{}'.format(line, line))
   return res

def generate_declarations(gl_syms):
   return ['RGLSYM' + x.upper() + 'PROC ' + '__rglgen_' + x + ';' for x in gl_syms]

def generate_macros(gl_syms):
   return ['    SYM(' + x.replace('gl', '') + '),' for x in gl_syms]

def dump(f, lines):
   f.write('\n'.join(lines))
   f.write('\n\n')

if __name__ == '__main__':
   with open(sys.argv[1], 'r') as f:
      lines = f.readlines()
      typedefs, syms = find_gl_symbols(lines)

      overrides = generate_defines(syms)
      declarations = generate_declarations(syms)
      externs = ['extern ' + x for x in declarations]

      macros = generate_macros(syms)

   with open(sys.argv[2], 'w') as f:
      f.write('#ifndef RGLGEN_DECL_H__\n')
      f.write('#define RGLGEN_DECL_H__\n')
      dump(f, typedefs)
      dump(f, overrides)
      dump(f, externs)
      f.write('struct rglgen_sym_map { const char *sym; void *ptr; };\n')
      f.write('extern const struct rglgen_sym_map rglgen_symbol_map[];\n')
      f.write('#endif\n')

   with open(sys.argv[3], 'w') as f:
      f.write('#include "glsym.h"\n')
      f.write('#include <stddef.h>\n')
      f.write('#define SYM(x) { "gl" #x, &(gl##x) }\n')
      f.write('const struct rglgen_sym_map rglgen_symbol_map[] = {\n')
      dump(f, macros)
      f.write('    { NULL, NULL },\n')
      f.write('};\n')
      dump(f, declarations)

