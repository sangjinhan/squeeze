" Based on https://github.com/shiracamus/vim-syntax-x86-objdump-d/

if exists("b:current_syntax")
  finish
endif

syntax match objdumpOffset     "[+-]"
syntax match objdumpNumber     "[+-]\?\<0x[0-9a-f]\+\>" contains=objdumpOffset
syntax match objdumpNumber     "[+-]\?\<[0-9a-f]\+\>" contains=objdumpOffset

syntax match objdumpRegister   "\<[re]\?[abcd][xhl]\>"
syntax match objdumpRegister   "\<[re]\?[sd]il\?\>"
syntax match objdumpRegister   "\<[re]\?[sbi]pl\?\>"
syntax match objdumpRegister   "\<r[0-9]\+[dwb]\?\>"
syntax match objdumpRegister   "[^\t]\<[cdefgs]s\>"hs=s+1

syntax match objdumpAt         "@"
syntax match objdumpSection    " \.[a-z][a-z_\.-]*:"he=e-1
syntax match objdumpSection    "@[a-z0-9_][a-z0-9_-]\+"hs=s+1 contains=objdumpAt,objdumpNumber

syntax match objdumpLabel      "<[a-z0-9_.][a-z0-9_.@+-]\+>"hs=s+1,he=e-1 contains=objdumpNumber,objdumpSection
syntax match objdumpHexDump    ":\t\([0-9a-f][0-9a-f][ \t]\)\+"hs=s+1

syntax match objdumpError      "<internal disassembler error>"
syntax match objdumpError      "(bad)"

syntax keyword objdumpTodo     contained TODO

syntax region objdumpComment   start="/\*" end="\*/" contains=objdumpTodo
syntax match objdumpComment    "[#;!|].*" contains=objdumpLabel,objdumpTodo
syntax match objdumpStatement  "//.*" contains=cStatement

syntax match objdumpSpecial    display contained "\\\(x\x\+\|\o\{1,3}\|.\|$\)"
syntax region objdumpString    start=+"+ skip=+\\\\\|\\"\|\\$+ excludenl end=+"+ end=+$+ keepend contains=objdumpSpecial
syntax region objdumpString    start=+'+ skip=+\\\\\|\\'\|\\$+ excludenl end=+'+ end=+$+ keepend contains=objdumpSpecial

syntax match objdumpFormat     ": \+file format "
syntax match objdumpTitle      "^[^ ]\+: \+file format .*$" contains=objdumpFormat

syntax match objdumpMacro      "FWORD"
syntax match objdumpMacro      "QWORD"
syntax match objdumpMacro      "DWORD"
syntax match objdumpMacro      "BYTE"
syntax match objdumpMacro      "PTR"

syntax match objdumpData       ".word"
syntax match objdumpData       ".short"
syntax match objdumpData       ".byte"

syntax match objdumpOpecode    "\<add "
syntax match objdumpOpecode    "\<adc "
syntax match objdumpOpecode    "\<dec "
syntax match objdumpOpecode    "\<fadd "

highlight default link objdumpComment     Comment
highlight default link objdumpNumber      Number
highlight default link objdumpString      String
highlight default link objdumpHexDump     Identifier
highlight default link objdumpStatement   Statement
highlight default link objdumpLabel       Label
highlight default link objdumpData        Define
highlight default link objdumpMacro       Macro
highlight default link objdumpRegister    StorageClass
highlight default link objdumpTitle       Typedef
highlight default link objdumpSpecial     SpecialChar
highlight default link objdumpSection     Special
highlight default link objdumpError       Error
highlight default link objdumpTodo        Todo

let b:current_syntax = "objdump"

" vim: ts=8 sw=2 sts=2
