/*global Bloodhound */
const materialEngine = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: materialsUrl,
});

const materialaliasEngine = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: materialAliasesUrl,
});

$('.typeahead-materials').typeahead({
        hint: true,
        highlight: true,
        minLength: 1,
        autoselect: true,
    }, {
        name: 'materialaliases',
        source: materialaliasEngine,
        display: 'name',
        templates: {
            suggestion: function (e) {
                if (e.material.images.length > 0) {
                    imgHtml = `<div class="tt-suggestion-image float-right"><img src="${e.material.images[0]}"></div>`;
                } else {
                    imgHtml = `<div class="tt-suggestion-image tt-suggestion-no-image"></div>`;
                }
                return `<div class="clearfix">
                            ${imgHtml}
                            <div class="tt-suggestion-text">
                                <div class="tt-suggestion-name" data-id="${e.material.id}">${e.name}</div>
                                <div class="tt-suggestion-alias">${e.material.name}</div>
                                <div class="clearfix">
                                    <div class="tt-suggestion-category">${(e.material.categories.length > 0 ? e.material.categories[0] : "")}</div>
                                    ${(e.material.gm === true ? '<div class="tt-suggestion-gm">GM</div>' : '')}
                                </div>
                            </div>
                        </div>`;
            }
        }
    }
    , {
        name: 'materials',
        source: materialEngine,
        display: 'name',
        templates: {
            suggestion: function (e) {
                if (e.images.length > 0) {
                    imgHtml = `<div class="tt-suggestion-image float-right"><img src="${e.images[0]}"></div>`;
                } else {
                    imgHtml = `<div class="tt-suggestion-image tt-suggestion-no-image"></div>`;
                }
                return `<div class="clearfix">
                            ${imgHtml}
                            <div class="tt-suggestion-text">
                                <div class="tt-suggestion-name" data-id="${e.id}">${e.name}</div>
                                <div class="clearfix">
                                    <div class="tt-suggestion-category">${(e.categories.length > 0 ? e.categories[0] : "")}</div>
                                    ${(e.gm === true ? '<div class="tt-suggestion-gm">GM</div>' : '')}
                                </div>
                            </div>
                        </div>`;
            }
        }
    });
