local f=assert(io.open(pandoc.path.directory(PANDOC_SCRIPT_FILE).."/canonical-reference-map.json","r"))
local labels=pandoc.json.decode(f:read("*a")); f:close()
function Inlines(items)
 local result=pandoc.List()
 for _,item in ipairs(items) do
  local convert=item.t=="Cite" and #item.citations>0
  if convert then for _,c in ipairs(item.citations) do if not c.id:match("^tbl:") then convert=false end end end
  if not convert then result:insert(item) else
   local previous=pandoc.utils.stringify(result):lower()
   local kind=not (previous:match("table%s*$") or previous:match("tables%s*$") or previous:match("tbl%.%s*$"))
   for index,c in ipairs(item.citations) do
    local number=assert(labels[c.id],"canonical table label missing: "..c.id)
    if index>1 then result:insert(pandoc.Str(";"));result:insert(pandoc.Space()) end
    result:extend(c.prefix)
    if #c.prefix>0 then result:insert(pandoc.Space()) end
    result:insert(pandoc.Link((kind and "Table " or "")..number,"../web/index.html#"..c.id))
    if #c.suffix>0 then result:insert(pandoc.Space());result:extend(c.suffix) end
   end
  end
 end
 return result
end
function Pandoc(doc)
 local current=nil
 for _,block in ipairs(doc.blocks) do
  if block.t=="Div" and block.identifier:match("^tbl:") then current=assert(labels[block.identifier],"table anchor absent from canonical map") end
  if current and block.t=="Header" and block.identifier:match("^dr%-slide%-.*%-table%-") then
   local text=pandoc.utils.stringify(block.content)
   text=text:gsub("^Table %d+","Table "..current,1)
   block.content=pandoc.Inlines{pandoc.Str(text)}
  end
 end
 return doc
end
