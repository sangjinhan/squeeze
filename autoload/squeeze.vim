let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

function! squeeze#SqueezeToggle()
	call s:Toggle()
endfunction

function! s:Python(fn)
	if s:python_version == 3
		exec "python3 ". a:fn
    elseif s:python_version == 2
		exec "python ". a:fn
	endif
endfunction

function! s:TimerHandler(...)
    call s:Python('poll_result()')
endfunction

function! s:FailToInitialize(msg)
	function! s:DidNotLoad()
		echohl WarningMsg|echomsg s:error_msg|echohl None
	endfunction
    let s:error_msg = a:msg
	command! -nargs=0 SqueezeToggle call s:DidNotLoad()
endfunction

" returns a non-zero if initialization succeeded.
function! s:Initialize()
	if exists('g:squeeze_initialized')
		return 1
	endif

    if v:version < 800
        call s:FailToInitialize('Squeeze requires Vim 8 or later')
		return 0
    endif

	if has('python3')
		let s:python_version = 3
	elseif has('python')"
		let s:python_version = 2
	else
		function! s:DidNotLoad()
			echohl WarningMsg|echomsg "Squeeze requires Vim to be compiled with Python 2 or 3"|echohl None
		endfunction
		command! -nargs=0 SqueezeToggle call s:DidNotLoad()
		return 0
	endif

    call s:Python('sys.path.insert(1, "'. s:plugin_path .'")')

    if s:python_version == 3
		exec 'py3file ' . escape(s:plugin_path, ' ') . '/squeeze.py'
    else
		exec 'pyfile ' . escape(s:plugin_path, ' ') . '/squeeze.py'
    endif

	let g:squeeze_initialized = 1
    return 1
endfunction

function! s:Toggle()
	if s:Initialize()
	    call s:Python('toggle()')
    else
        call s:DidNotLoad()
    endif
endfunction
