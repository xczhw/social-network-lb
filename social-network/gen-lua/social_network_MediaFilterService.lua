--
-- Autogenerated by Thrift
--
-- DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
-- @generated
--


require 'Thrift'
require 'social_network_ttypes'

MediaFilterServiceClient = __TObject.new(__TClient, {
  __type = 'MediaFilterServiceClient'
})

function MediaFilterServiceClient:UploadMedia(req_id, media_types, medium, carrier)
  self:send_UploadMedia(req_id, media_types, medium, carrier)
  return self:recv_UploadMedia(req_id, media_types, medium, carrier)
end

function MediaFilterServiceClient:send_UploadMedia(req_id, media_types, medium, carrier)
  self.oprot:writeMessageBegin('UploadMedia', TMessageType.CALL, self._seqid)
  local args = UploadMedia_args:new{}
  args.req_id = req_id
  args.media_types = media_types
  args.medium = medium
  args.carrier = carrier
  args:write(self.oprot)
  self.oprot:writeMessageEnd()
  self.oprot.trans:flush()
end

function MediaFilterServiceClient:recv_UploadMedia(req_id, media_types, medium, carrier)
  local fname, mtype, rseqid = self.iprot:readMessageBegin()
  if mtype == TMessageType.EXCEPTION then
    local x = TApplicationException:new{}
    x:read(self.iprot)
    self.iprot:readMessageEnd()
    error(x)
  end
  local result = UploadMedia_result:new{}
  result:read(self.iprot)
  self.iprot:readMessageEnd()
  if result.success ~= nil then
    return result.success
  elseif result.se then
    error(result.se)
  end
  error(TApplicationException:new{errorCode = TApplicationException.MISSING_RESULT})
end
MediaFilterServiceIface = __TObject:new{
  __type = 'MediaFilterServiceIface'
}


MediaFilterServiceProcessor = __TObject.new(__TProcessor
, {
 __type = 'MediaFilterServiceProcessor'
})

function MediaFilterServiceProcessor:process(iprot, oprot, server_ctx)
  local name, mtype, seqid = iprot:readMessageBegin()
  local func_name = 'process_' .. name
  if not self[func_name] or ttype(self[func_name]) ~= 'function' then
    iprot:skip(TType.STRUCT)
    iprot:readMessageEnd()
    x = TApplicationException:new{
      errorCode = TApplicationException.UNKNOWN_METHOD
    }
    oprot:writeMessageBegin(name, TMessageType.EXCEPTION, seqid)
    x:write(oprot)
    oprot:writeMessageEnd()
    oprot.trans:flush()
  else
    self[func_name](self, seqid, iprot, oprot, server_ctx)
  end
end

function MediaFilterServiceProcessor:process_UploadMedia(seqid, iprot, oprot, server_ctx)
  local args = UploadMedia_args:new{}
  local reply_type = TMessageType.REPLY
  args:read(iprot)
  iprot:readMessageEnd()
  local result = UploadMedia_result:new{}
  local status, res = pcall(self.handler.UploadMedia, self.handler, args.req_id, args.media_types, args.medium, args.carrier)
  if not status then
    reply_type = TMessageType.EXCEPTION
    result = TApplicationException:new{message = res}
  elseif ttype(res) == 'ServiceException' then
    result.se = res
  else
    result.success = res
  end
  oprot:writeMessageBegin('UploadMedia', reply_type, seqid)
  result:write(oprot)
  oprot:writeMessageEnd()
  oprot.trans:flush()
end

-- HELPER FUNCTIONS AND STRUCTURES

UploadMedia_args = __TObject:new{
  req_id,
  media_types,
  medium,
  carrier
}

function UploadMedia_args:read(iprot)
  iprot:readStructBegin()
  while true do
    local fname, ftype, fid = iprot:readFieldBegin()
    if ftype == TType.STOP then
      break
    elseif fid == 1 then
      if ftype == TType.I64 then
        self.req_id = iprot:readI64()
      else
        iprot:skip(ftype)
      end
    elseif fid == 2 then
      if ftype == TType.LIST then
        self.media_types = {}
        local _etype365, _size362 = iprot:readListBegin()
        for _i=1,_size362 do
          local _elem366 = iprot:readString()
          table.insert(self.media_types, _elem366)
        end
        iprot:readListEnd()
      else
        iprot:skip(ftype)
      end
    elseif fid == 3 then
      if ftype == TType.LIST then
        self.medium = {}
        local _etype370, _size367 = iprot:readListBegin()
        for _i=1,_size367 do
          local _elem371 = iprot:readString()
          table.insert(self.medium, _elem371)
        end
        iprot:readListEnd()
      else
        iprot:skip(ftype)
      end
    elseif fid == 4 then
      if ftype == TType.MAP then
        self.carrier = {}
        local _ktype373, _vtype374, _size372 = iprot:readMapBegin() 
        for _i=1,_size372 do
          local _key376 = iprot:readString()
          local _val377 = iprot:readString()
          self.carrier[_key376] = _val377
        end
        iprot:readMapEnd()
      else
        iprot:skip(ftype)
      end
    else
      iprot:skip(ftype)
    end
    iprot:readFieldEnd()
  end
  iprot:readStructEnd()
end

function UploadMedia_args:write(oprot)
  oprot:writeStructBegin('UploadMedia_args')
  if self.req_id ~= nil then
    oprot:writeFieldBegin('req_id', TType.I64, 1)
    oprot:writeI64(self.req_id)
    oprot:writeFieldEnd()
  end
  if self.media_types ~= nil then
    oprot:writeFieldBegin('media_types', TType.LIST, 2)
    oprot:writeListBegin(TType.STRING, #self.media_types)
    for _,iter378 in ipairs(self.media_types) do
      oprot:writeString(iter378)
    end
    oprot:writeListEnd()
    oprot:writeFieldEnd()
  end
  if self.medium ~= nil then
    oprot:writeFieldBegin('medium', TType.LIST, 3)
    oprot:writeListBegin(TType.STRING, #self.medium)
    for _,iter379 in ipairs(self.medium) do
      oprot:writeString(iter379)
    end
    oprot:writeListEnd()
    oprot:writeFieldEnd()
  end
  if self.carrier ~= nil then
    oprot:writeFieldBegin('carrier', TType.MAP, 4)
    oprot:writeMapBegin(TType.STRING, TType.STRING, ttable_size(self.carrier))
    for kiter380,viter381 in pairs(self.carrier) do
      oprot:writeString(kiter380)
      oprot:writeString(viter381)
    end
    oprot:writeMapEnd()
    oprot:writeFieldEnd()
  end
  oprot:writeFieldStop()
  oprot:writeStructEnd()
end

UploadMedia_result = __TObject:new{
  success,
  se
}

function UploadMedia_result:read(iprot)
  iprot:readStructBegin()
  while true do
    local fname, ftype, fid = iprot:readFieldBegin()
    if ftype == TType.STOP then
      break
    elseif fid == 0 then
      if ftype == TType.LIST then
        self.success = {}
        local _etype385, _size382 = iprot:readListBegin()
        for _i=1,_size382 do
          local _elem386 = iprot:readBool()
          table.insert(self.success, _elem386)
        end
        iprot:readListEnd()
      else
        iprot:skip(ftype)
      end
    elseif fid == 1 then
      if ftype == TType.STRUCT then
        self.se = ServiceException:new{}
        self.se:read(iprot)
      else
        iprot:skip(ftype)
      end
    else
      iprot:skip(ftype)
    end
    iprot:readFieldEnd()
  end
  iprot:readStructEnd()
end

function UploadMedia_result:write(oprot)
  oprot:writeStructBegin('UploadMedia_result')
  if self.success ~= nil then
    oprot:writeFieldBegin('success', TType.LIST, 0)
    oprot:writeListBegin(TType.BOOL, #self.success)
    for _,iter387 in ipairs(self.success) do
      oprot:writeBool(iter387)
    end
    oprot:writeListEnd()
    oprot:writeFieldEnd()
  end
  if self.se ~= nil then
    oprot:writeFieldBegin('se', TType.STRUCT, 1)
    self.se:write(oprot)
    oprot:writeFieldEnd()
  end
  oprot:writeFieldStop()
  oprot:writeStructEnd()
end