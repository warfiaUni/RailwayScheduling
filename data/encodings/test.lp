% choose direction
{direction(D,T,ID):cell((X,Y),O,D)}=1 :- limit(L), 
                                    T<L, 
                                    not done(ID,T),
                                    trans(ID,_,(X,Y),O,T). 

% start path
1{trans(ID,(X,Y),(X+A,Y+B),O,0):diff(D,A,B)}1 :- cell((X,Y),O,D), 
                                            schedule(ID,(X,Y),(_,_),O).

% continue path
trans(ID,(X,Y),(X+A,Y+B),D,T+1) :- trans(ID,_,(X,Y),_,T), 
                                direction(D,T,ID), 
                                diff(D,A,B).

% reached target?
done(ID,T) :- schedule(_,_,(X,Y),_), trans(ID,_,(X,Y),_,T).

% Display the result
#show trans/5.
#show done/2.
%#show sln/4.