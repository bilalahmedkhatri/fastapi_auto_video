x="hello world java"
a=x.split(" ")
b=a[0]
c=a.splice(1)
k=c.map((e)=>{
    f=e.split("")
    f[0]=f[0].toLocaleUpperCase()
    g=f.join("")
    return g
})
s=b+k.join("")