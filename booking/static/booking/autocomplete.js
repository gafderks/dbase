var engine = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: materialsUrl,
});

$('.typeahead-materials').typeahead({
    hint: true,
    highlight: true,
    minLength: 1,
    autoselect: true,
}, {
    name: 'materials',
    source: engine,
    display: 'name',
    templates: {
        suggestion: function (e) {
            if (e.images.length > 0) {
                imgHtml = '<div class="tt-suggestion-image float-right"><img src="' + e.images[0] + '"></div>';
            } else {
                imgHtml = '<div class="tt-suggestion-image tt-suggestion-no-image"></div>'
            }
            return [
                '<div class="clearfix">',
                    imgHtml,
                    '<div class="tt-suggestion-text">',
                        '<div class="tt-suggestion-name" data-id="' + e.id + '">' + e.name + '</div>',
                        '<div class="clearfix">',
                            '<div class="tt-suggestion-category">' + (e.categories.length > 0 ? e.categories[0] : "") + '</div>',
                            (e.gm === true ? '<div class="tt-suggestion-gm">GM</div>' : ''),
                        '</div>',
                    '</div>',
                '</div>'
            ].join('\n');
        }
    }
});
