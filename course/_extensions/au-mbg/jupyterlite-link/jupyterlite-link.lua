local function stringify(value)
  if value == nil then
    return nil
  end

  local s = pandoc.utils.stringify(value)
  if s == "" then
    return nil
  end

  return s
end

local function meta_bool(value)
  local s = stringify(value)
  if s == nil then
    return false
  end

  s = s:lower()
  return s == "true" or s == "1" or s == "yes"
end

local function abort(message)
  io.stderr:write("ERROR: " .. message .. "\n")
  os.exit(1)
end

local function trim_slashes(value)
  return value:gsub("^/+", ""):gsub("/+$", "")
end

local function percent_encode(value)
  return tostring(value):gsub("([^%w%-_%.~])", function(character)
    return string.format("%%%02X", string.byte(character))
  end)
end

local function encode_path(value)
  return tostring(value):gsub("([^%w%-_%.~/])", function(character)
    return string.format("%%%02X", string.byte(character))
  end)
end

local function js_string(value)
  value = tostring(value)
  value = value:gsub("\\", "\\\\")
  value = value:gsub("'", "\\'")
  value = value:gsub("\r", "\\r")
  value = value:gsub("\n", "\\n")
  value = value:gsub("</", "<\\/")
  return "'" .. value .. "'"
end

local function basename_without_extension(path)
  if path == nil or path == "" then
    return nil
  end

  local filename = path:match("([^/]+)$") or path
  return filename:gsub("%.[^.]+$", "")
end

local function document_basename()
  local candidates = {}

  if quarto.doc then
    if type(quarto.doc.project_output_file) == "function" then
      table.insert(candidates, quarto.doc.project_output_file())
    end
    table.insert(candidates, quarto.doc.output_file)
    table.insert(candidates, quarto.doc.input_file)
  end

  for _, candidate in ipairs(candidates) do
    local base = basename_without_extension(candidate)
    if base ~= nil and base ~= "" then
      return base
    end
  end

  abort("jupyterlite-link: could not determine the current document filename.")
end

local function jupyterlite_config()
  local url = stringify(quarto.metadata.get("teaching.jupyterlite.url"))
  local repo = stringify(quarto.metadata.get("teaching.jupyterlite.repo"))
  local branch = stringify(quarto.metadata.get("teaching.jupyterlite.branch")) or "built-notebooks"
  local root = stringify(quarto.metadata.get("teaching.jupyterlite.root")) or "built_notebooks"
  local notebook_profile = stringify(quarto.metadata.get("teaching.jupyterlite.notebook-profile")) or "student"
  local course_directory = stringify(quarto.metadata.get("teaching.jupyterlite.course-directory"))
  local text = stringify(quarto.metadata.get("teaching.jupyterlite.text")) or "Open in JupyterLite"
  local icon = stringify(quarto.metadata.get("teaching.jupyterlite.icon")) or "box-arrow-up-right"

  if url == nil then
    abort("jupyterlite-link: documents with 'jupyterlite: true' require 'teaching.jupyterlite.url'.")
  end

  if not url:match("^https?://[^%s]+$") then
    abort("jupyterlite-link: 'teaching.jupyterlite.url' must be an absolute HTTP or HTTPS URL.")
  end

  if repo == nil then
    abort("jupyterlite-link: documents with 'jupyterlite: true' require 'teaching.jupyterlite.repo: owner/repo'.")
  end

  if not repo:match("^[^/%s]+/[^/%s]+$") then
    abort("jupyterlite-link: 'teaching.jupyterlite.repo' must be in 'owner/repo' form.")
  end

  if course_directory ~= nil then
    course_directory = trim_slashes(course_directory)
    if course_directory == "" then
      course_directory = nil
    end
  end

  return {
    url = url,
    repo = trim_slashes(repo),
    branch = trim_slashes(branch),
    root = trim_slashes(root),
    notebook_profile = trim_slashes(notebook_profile),
    course_directory = course_directory,
    text = text,
    icon = icon,
  }
end

local function raw_notebook_url(config)
  local notebook = document_basename() .. ".ipynb"
  local path = table.concat({
    config.repo,
    config.branch,
    config.root,
    config.notebook_profile,
    notebook,
  }, "/")

  return "https://raw.githubusercontent.com/" .. encode_path(path)
end

local function append_query(url, query)
  local base, fragment = url:match("^(.-)(#.*)$")
  if base == nil then
    base = url
    fragment = ""
  end

  local separator = "?"
  if base:find("?", 1, true) then
    local final_character = base:sub(-1)
    separator = (final_character == "?" or final_character == "&") and "" or "&"
  end

  return base .. separator .. query .. fragment
end

local function jupyterlite_url(config)
  local query = "fromURL=" .. percent_encode(raw_notebook_url(config))
  if config.course_directory ~= nil then
    query = query .. "&fromURLToFolder=" .. percent_encode(config.course_directory)
  end
  return append_query(config.url, query)
end

local function injection_script(url, text, icon)
  return string.format([[
<script>
document.addEventListener('DOMContentLoaded', function () {
  const url = %s;
  const text = %s;
  const icon = %s;

  function createItem() {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = url;
    const iconEl = document.createElement('i');
    iconEl.className = 'bi bi-' + icon;
    link.appendChild(iconEl);
    link.appendChild(document.createTextNode(text));
    item.appendChild(link);
    return item;
  }

  function hasLink(container) {
    if (!container) {
      return false;
    }
    return Array.from(container.querySelectorAll('a')).some(function (link) {
      return link.href === url || link.getAttribute('href') === url;
    });
  }

  const formats = document.querySelector('.quarto-alternate-formats');
  if (formats) {
    let list = formats.querySelector('ul');
    if (!list) {
      list = document.createElement('ul');
      formats.appendChild(list);
    }
    if (!hasLink(list)) {
      list.appendChild(createItem());
    }
    return;
  }

  const block = document.createElement('div');
  block.className = 'quarto-alternate-formats';
  const heading = document.createElement('h2');
  heading.textContent = 'Other Formats';
  const list = document.createElement('ul');
  list.appendChild(createItem());
  block.appendChild(heading);
  block.appendChild(list);

  const margin = document.querySelector('#quarto-margin-sidebar');
  if (margin) {
    margin.appendChild(block);
    return;
  }

  const main = document.querySelector('main');
  if (main) {
    main.insertBefore(block, main.firstChild);
    return;
  }

  document.body.insertBefore(block, document.body.firstChild);
});
</script>
]], js_string(url), js_string(text), js_string(icon))
end

function Pandoc(doc)
  if not quarto.doc.is_format("html") then
    return doc
  end

  if not meta_bool(doc.meta.jupyterlite) then
    return doc
  end

  local config = jupyterlite_config()
  local url = jupyterlite_url(config)
  local script = injection_script(url, config.text, config.icon)

  table.insert(doc.blocks, 1, pandoc.RawBlock("html", script))
  return doc
end
