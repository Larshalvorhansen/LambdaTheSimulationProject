function error = ci(data,interval)
if size(data,1)>1
error=abs(quantile(data,interval)-mean(data));
else
    error=zeros(size(data));
end
end

