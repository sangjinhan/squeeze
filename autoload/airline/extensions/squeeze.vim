function! airline#extensions#squeeze#statusline(...)
    " let builder = a:1
    " let context = a:2
    if &filetype == 'squeeze'
        let w:airline_section_a = 'Squeeze'
        let w:airline_section_b = '%t'
        let w:airline_section_c = 'Compiler arguments: '. w:squeeze_args
        let g:airline_variable_referenced_in_statusline = 'foo'
    endif
    return 0
endfunction

function! airline#extensions#squeeze#inactive_statusline(...)
    if &filetype == 'squeeze'
        let w:airline_section_a = 'Squeeze'
        let w:airline_section_b = 'hello'
        let w:airline_section_c = '%f'
        let g:airline_variable_referenced_in_statusline = 'bar'
    endif
    return 0
endfunction

function! airline#extensions#squeeze#init(...)
    call airline#add_statusline_func('airline#extensions#squeeze#statusline')
    call airline#add_inactive_statusline_func('airline#extensions#squeeze#inactive_statusline')
endfunction
