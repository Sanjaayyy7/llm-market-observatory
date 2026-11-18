-- Exposure window per priced canonical model; read by the G6 sensitivity and verified-only KM.
with {{ exposure_ctes() }}

select * from exposure
