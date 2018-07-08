if !exists('g:squeeze_debug') && (exists('g:squeeze_disable') && g:squeeze_disable == 1 || exists('loaded_squeeze') || &cp)
    finish
endif
let loaded_squeeze = 1

command! -nargs=0 SqueezeToggle call squeeze#SqueezeToggle()
