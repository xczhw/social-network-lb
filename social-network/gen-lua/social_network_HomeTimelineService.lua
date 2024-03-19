--
-- Autogenerated by Thrift
--
-- DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
-- @generated
--


local Thrift = require 'Thrift'
local TType = Thrift.TType
local TMessageType = Thrift.TMessageType
local __TObject = Thrift.__TObject
local TApplicationException = Thrift.TApplicationException
local __TClient = Thrift.__TClient
local __TProcessor = Thrift.__TProcessor
local ttype = Thrift.ttype
local ttable_size = Thrift.ttable_size
local social_network_ttypes = require 'social_network_ttypes'
local ServiceException = social_network_ttypes.ServiceException
local Post = social_network_ttypes.Post

-- HELPER FUNCTIONS AND STRUCTURES

local ReadHomeTimeline_args = __TObject:new{
  req_id,
  user_id,
  start,
  stop,
  carrier
}

function ReadHomeTimeline_args:read(iprot)
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
      if ftype == TType.I64 then
        self.user_id = iprot:readI64()
      else
        iprot:skip(ftype)
      end
    elseif fid == 3 then
      if ftype == TType.I32 then
        self.start = iprot:readI32()
      else
        iprot:skip(ftype)
      end
    elseif fid == 4 then
      if ftype == TType.I32 then
        self.stop = iprot:readI32()
      else
        iprot:skip(ftype)
      end
    elseif fid == 5 then
      if ftype == TType.MAP then
        self.carrier = {}
        local _ktype193, _vtype194, _size192 = iprot:readMapBegin() 
        for _i=1,_size192 do
          local _key196 = iprot:readString()
          local _val197 = iprot:readString()
          self.carrier[_key196] = _val197
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

function ReadHomeTimeline_args:write(oprot)
  oprot:writeStructBegin('ReadHomeTimeline_args')
  if self.req_id ~= nil then
    oprot:writeFieldBegin('req_id', TType.I64, 1)
    oprot:writeI64(self.req_id)
    oprot:writeFieldEnd()
  end
  if self.user_id ~= nil then
    oprot:writeFieldBegin('user_id', TType.I64, 2)
    oprot:writeI64(self.user_id)
    oprot:writeFieldEnd()
  end
  if self.start ~= nil then
    oprot:writeFieldBegin('start', TType.I32, 3)
    oprot:writeI32(self.start)
    oprot:writeFieldEnd()
  end
  if self.stop ~= nil then
    oprot:writeFieldBegin('stop', TType.I32, 4)
    oprot:writeI32(self.stop)
    oprot:writeFieldEnd()
  end
  if self.carrier ~= nil then
    oprot:writeFieldBegin('carrier', TType.MAP, 5)
    oprot:writeMapBegin(TType.STRING, TType.STRING, ttable_size(self.carrier))
    for kiter198,viter199 in pairs(self.carrier) do
      oprot:writeString(kiter198)
      oprot:writeString(viter199)
    end
    oprot:writeMapEnd()
    oprot:writeFieldEnd()
  end
  oprot:writeFieldStop()
  oprot:writeStructEnd()
end

local ReadHomeTimeline_result = __TObject:new{
  success,
  se
}

function ReadHomeTimeline_result:read(iprot)
  iprot:readStructBegin()
  while true do
    local fname, ftype, fid = iprot:readFieldBegin()
    if ftype == TType.STOP then
      break
    elseif fid == 0 then
      if ftype == TType.LIST then
        self.success = {}
        local _etype203, _size200 = iprot:readListBegin()
        for _i=1,_size200 do
          local _elem204 = Post:new{}
          _elem204:read(iprot)
          table.insert(self.success, _elem204)
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

function ReadHomeTimeline_result:write(oprot)
  oprot:writeStructBegin('ReadHomeTimeline_result')
  if self.success ~= nil then
    oprot:writeFieldBegin('success', TType.LIST, 0)
    oprot:writeListBegin(TType.STRUCT, #self.success)
    for _,iter205 in ipairs(self.success) do
      iter205:write(oprot)
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

local HomeTimelineServiceClient = __TObject.new(__TClient, {
  __type = 'HomeTimelineServiceClient'
})

function HomeTimelineServiceClient:ReadHomeTimeline(req_id, user_id, start, stop, carrier)
  self:send_ReadHomeTimeline(req_id, user_id, start, stop, carrier)
  return self:recv_ReadHomeTimeline(req_id, user_id, start, stop, carrier)
end

function HomeTimelineServiceClient:send_ReadHomeTimeline(req_id, user_id, start, stop, carrier)
  self.oprot:writeMessageBegin('ReadHomeTimeline', TMessageType.CALL, self._seqid)
  local args = ReadHomeTimeline_args:new{}
  args.req_id = req_id
  args.user_id = user_id
  args.start = start
  args.stop = stop
  args.carrier = carrier
  args:write(self.oprot)
  self.oprot:writeMessageEnd()
  self.oprot.trans:flush()
end

function HomeTimelineServiceClient:recv_ReadHomeTimeline(req_id, user_id, start, stop, carrier)
  local fname, mtype, rseqid = self.iprot:readMessageBegin()
  if mtype == TMessageType.EXCEPTION then
    local x = TApplicationException:new{}
    x:read(self.iprot)
    self.iprot:readMessageEnd()
    error(x)
  end
  local result = ReadHomeTimeline_result:new{}
  result:read(self.iprot)
  self.iprot:readMessageEnd()
  if result.success ~= nil then
    return result.success
  elseif result.se then
    error(result.se)
  end
  error(TApplicationException:new{errorCode = TApplicationException.MISSING_RESULT})
end
local HomeTimelineServiceIface = __TObject:new{
  __type = 'HomeTimelineServiceIface'
}


local HomeTimelineServiceProcessor = __TObject.new(__TProcessor
, {
 __type = 'HomeTimelineServiceProcessor'
})

function HomeTimelineServiceProcessor:process(iprot, oprot, server_ctx)
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

function HomeTimelineServiceProcessor:process_ReadHomeTimeline(seqid, iprot, oprot, server_ctx)
  local args = ReadHomeTimeline_args:new{}
  local reply_type = TMessageType.REPLY
  args:read(iprot)
  iprot:readMessageEnd()
  local result = ReadHomeTimeline_result:new{}
  local status, res = pcall(self.handler.ReadHomeTimeline, self.handler, args.req_id, args.user_id, args.start, args.stop, args.carrier)
  if not status then
    reply_type = TMessageType.EXCEPTION
    result = TApplicationException:new{message = res}
  elseif ttype(res) == 'ServiceException' then
    result.se = res
  else
    result.success = res
  end
  oprot:writeMessageBegin('ReadHomeTimeline', reply_type, seqid)
  result:write(oprot)
  oprot:writeMessageEnd()
  oprot.trans:flush()
end

return HomeTimelineServiceClient

