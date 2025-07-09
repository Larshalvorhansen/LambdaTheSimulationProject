function Y = forecast_vecm(Y0,horizon,p,r)
    
    % Define and estimate the model
    mod=vecm(size(Y0,2),r,p);
    vec=estimate(mod,Y0(p+2:end,:),'Y0',Y0(1:p+1,:));
    
    % Forecast the model
    Y=forecast(vec,horizon,Y0(end-p:end,:));
end