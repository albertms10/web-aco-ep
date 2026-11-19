const params = new URLSearchParams(window.location.search);

$("#taula-orgues")
  .bootstrapTable({
    classes: "table table-striped table-sm table-hover",
    headerStyle: function () {
      return { css: {}, classes: "taula-orgues-header" };
    },
    locale: "ca-ES",
    onClickRow: function (row, element, field) {
      if ($(element).data("href") !== undefined) {
        document.location = $(element).data("href");
      }
    },
    pageSize: 10,
    pagination: true,
    search: true,
    searchAccentNeutralise: true,
    searchAlign: "left",
    searchHighlight: true,
    searchText: params.get("q") ?? "",
    showColumns: true,
    toggle: "table",
  })
  .on("search.bs.table", function (e, searchText) {
    const url = new URL(window.location);

    if (searchText) {
      url.searchParams.set("q", searchText);
    } else {
      url.searchParams.delete("q");
    }

    history.replaceState(null, "", url);
  });

function composicioSorter(a, b) {
  if (a.length == 0 && b.length > 0) {
    return -1;
  } else if (a.length > 0 && b.length == 0) {
    return 1;
  } else if (a.length == 0 && b.length == 0) {
    return 0;
  } else {
    var aa = a.split(" ")[0].replace(",", "");
    var bb = b.split(" ")[0].replace(",", "");
    return aa - bb;
  }
}
